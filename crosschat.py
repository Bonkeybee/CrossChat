"""Handles the discord<->game portion of crosschat"""
import logging
import re
import time
from collections import OrderedDict
from http import HTTPStatus
from os import system

import asyncio
import discord
import pyautogui
from better_profanity import profanity
from discord import HTTPException
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option, create_permission
from discord_slash.model import SlashCommandPermissionType, SlashCommandOptionType
from tendo import singleton

import settings
from lib.beans.message import Message
from lib.services.chat_log_service import parse_chat_log, load_chat_log
from lib.services.guild_service import get_guild_members
from lib.services.message_service import push_all, add_message
from lib.utils import constants

system('title ' + 'crosschat')
singleton.SingleInstance()

# noinspection PyArgumentList
logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.INFO,
    handlers=[
        logging.FileHandler(filename="log.log", mode='w'),
        logging.StreamHandler()
    ])
LOG = logging.getLogger(__name__)
LOG.info("Starting CROSSCHAT...")

profanity.load_censor_words()
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
slash = SlashCommand(bot, sync_commands=True)

USER_CHANNEL_IDS = {int(settings.load()['discord']['guild_crosschat_channel_id']): 'guild', int(settings.load()['discord']['officer_crosschat_channel_id']): 'officer'}


# noinspection PyBroadException
async def chat_log_to_discord_webhook(chat_log_file_option, starting_key, channel, webhook_url_option, embed_name, embed_channel_id_option, embed_message_id_option, bad_patterns, good_patterns):
    """Reads the World of Warcraft addon chat logs and pushes new messages to the Discord webhook and/or embed"""
    try:
        await bot.wait_until_ready()
        while True:
            messages = get_chat_log_messages(chat_log_file_option, starting_key, channel)
            if embed_name and embed_channel_id_option and embed_message_id_option:
                messages = await handle_embed(messages, embed_name, embed_channel_id_option, embed_message_id_option, bad_patterns, good_patterns)
            if messages:
                push_all(settings.load()['discord'][webhook_url_option], messages, channel)
            await asyncio.sleep(constants.CHAT_LOG_CYCLE_TIME)
    except Exception as e:
        LOG.exception('Unexpected exception: ' + repr(e), e, exc_info=True)
        for key in USER_CHANNEL_IDS:
            await bot.get_channel(key).send('Unexpected exception: ' + repr(e))


def get_chat_log_messages(chat_log_file_option, starting_key, channel):
    """Loads and parses the World of Warcraft chat log and returns a sorted list of message objects"""
    chat_log = load_chat_log(settings.load()['wow'][chat_log_file_option])
    data_start = None
    messages = []
    for index, line in enumerate(chat_log):
        if index < len(chat_log) - 1:
            if re.match(starting_key, chat_log[index]):
                data_start = index + 1
            if data_start is not None and ((index + data_start) % 4) == 0:
                timestamp, player, message = parse_chat_log(index, chat_log)
                add_message(messages, timestamp, player, message, channel)
    messages.sort()
    return messages


async def handle_embed(messages: list[Message], embed_name, embed_channel_id_option, embed_message_id_option, bad_patterns, good_patterns) -> list[Message]:
    """Process messages """
    if messages:
        if settings.load().has_section('state') and settings.load().has_option('state', embed_message_id_option):
            discord_message: discord.Message = await bot.get_channel(int(settings.load()['discord'][embed_channel_id_option])).fetch_message(int(settings.load()['state'][embed_message_id_option]))
            if not discord_message.embeds:
                return await create_or_update_embed(discord_message, [], messages, embed_name, embed_channel_id_option, embed_message_id_option, bad_patterns, good_patterns)
            old_messages = get_old_messages_from_embed(discord_message.embeds[0])
            old_messages.sort()
            return await create_or_update_embed(discord_message, old_messages, messages, embed_name, embed_channel_id_option, embed_message_id_option, bad_patterns, good_patterns)
        else:
            return await create_or_update_embed(None, [], messages, embed_name, embed_channel_id_option, embed_message_id_option, bad_patterns, good_patterns)
    else:
        await refresh_embed(embed_channel_id_option, embed_message_id_option)


async def create_or_update_embed(discord_message, old_messages, new_messages, embed_name, embed_channel_id_option, embed_message_id_option, bad_patterns, good_patterns):
    """Create or update a discord embed"""
    embedded_messages, non_embedded_messages = filter_new_messages(new_messages, bad_patterns, good_patterns)
    embed = discord.Embed(title=embed_name, description=new_messages[-1].timestamp)
    messages_to_embed = old_messages + embedded_messages
    messages_to_embed = list(OrderedDict.fromkeys(messages_to_embed))
    messages_to_embed.sort()
    message_map = {}
    for message in messages_to_embed:
        message_map[message.player] = message
    messages_to_embed = list(message_map.values())
    messages_to_embed.sort(reverse=True)
    add_embed_fields(messages_to_embed, embed)
    if discord_message:
        await discord_message.edit(embed=embed)
    else:
        discord_message = await bot.get_channel(int(settings.load()['discord'][embed_channel_id_option])).send(embed=embed)
        settings.load()['state'][embed_message_id_option] = str(discord_message.id)
        with open(constants.CONFIG_FILE, 'w') as configfile:
            settings.load().write(configfile)
    return non_embedded_messages


def filter_new_messages(new_messages, bad_patterns, good_patterns):
    """Filter the messages and return the messages that will and will not be embedded"""
    embedded_messages = []
    non_embedded_messages = []
    for message in new_messages:
        if has_bad_pattern(message, bad_patterns):
            continue
        if has_good_pattern(message, good_patterns):
            embedded_messages.append(message)
        else:
            non_embedded_messages.append(message)
    return embedded_messages, non_embedded_messages


def has_bad_pattern(message, bad_patterns):
    """Check if the message has any bad patterns"""
    for pattern in bad_patterns:
        if pattern.match(message.line):
            return True
    return False


def has_good_pattern(message, good_patterns):
    """Check if the message has any good patterns"""
    for pattern in good_patterns:
        if pattern.match(message.line):
            return True
    return False


async def refresh_embed(embed_channel_id_option, embed_message_id_option):
    """Refresh the messages in the embed with new timestamps"""
    if settings.load().has_section('state') and settings.load().has_option('state', embed_message_id_option):
        discord_message: discord.Message = await get_message_with_retry(int(settings.load()['discord'][embed_channel_id_option]), int(settings.load()['state'][embed_message_id_option]), 0)
        if not discord_message or not discord_message.embeds:
            return
        old_messages = get_old_messages_from_embed(discord_message.embeds[0])
        old_messages.sort(reverse=True)
        embed = discord.Embed(title=discord_message.embeds[0].title, description=discord_message.embeds[0].description)
        add_embed_fields(old_messages, embed)
        await discord_message.edit(embed=embed)


async def get_message_with_retry(channel_id, message_id, attempts):
    """Gets a discord message with 5 retries"""
    try:
        return await bot.get_channel(channel_id).fetch_message(message_id)
    except HTTPException as exception:
        if exception.code == HTTPStatus.GATEWAY_TIMEOUT and attempts <= constants.DISCORD_RETRY_LIMIT:
            await asyncio.sleep(pow(attempts + 1, 2))
            return await get_message_with_retry(channel_id, message_id, attempts + 1)


def get_old_messages_from_embed(discord_embed):
    """Parse the previously sent messages from the embed"""
    old_messages = []
    for field in discord_embed.fields:
        if field.name and field.value:
            timestamp = field.value.split('|')[-1]
            if any(c in 'abcdefABCDEF' for c in timestamp):
                timestamp_major = int(timestamp.split('.')[0], 16)
                timestamp_minor = int(timestamp.split('.')[1], 16)
                timestamp = str(timestamp_major) + '.' + str(timestamp_minor)
            player = field.name.strip()
            line = ':'.join(field.value.split(':')[1:]).strip()
            if line:
                message = Message(timestamp, player, line)
                old_messages.append(message)
    return old_messages


def add_embed_fields(old_messages, embed):
    """Add messages to the embed fields"""
    for message in old_messages:
        message.line = re.compile('\\b(tank|tanks)\\b', re.IGNORECASE).sub('<@&'+settings.load()['discord']['tank_role']+'>', message.line)
        message.line = re.compile('\\b(heal|heals|healer)\\b', re.IGNORECASE).sub('<@&'+settings.load()['discord']['heal_role']+'>', message.line)
        message.line = re.compile('\\b(dps)\\b', re.IGNORECASE).sub('<@&'+settings.load()['discord']['dps_role']+'>', message.line)
        message.line = re.compile('\\b(all)\\b', re.IGNORECASE).sub('<@&'+settings.load()['discord']['tank_role']+'><@&'+settings.load()['discord']['heal_role']+'><@&'+settings.load()['discord']['dps_role']+'>', message.line)
        duration = int((float(time.time()) - float(message.timestamp)) / 60)
        if duration <= 60:
            readable_duration = str(duration) + 'm: '
            if duration == 0:
                readable_duration = 'now: '
            timestamp_major = hex(int(message.timestamp.split('.')[0]))[2:]
            timestamp_minor = hex(int(message.timestamp.split('.')[1]))[2:]
            message.line = message.line.rsplit('|', 1)[0]

            count = 0
            for field in embed.fields:
                count += len(field.name) + len(field.value)
            if count < constants.DISCORD_EMBED_LIMIT:
                embed.add_field(name=message.player.strip(), value=((readable_duration + message.line).strip() + ' | ' + (timestamp_major + '.' + timestamp_minor).strip()), inline=True)
            else:
                return


# DISCORD STUFF
@bot.event
async def on_ready():
    """Indicator for when the bot connects to discord"""
    LOG.info(bot.user.name + ' has connected to Discord!')


async def handle_restart():
    """Send a key-combination on the host to trigger the Auto-Hotkey script reload"""
    pyautogui.keyDown('ctrl')
    pyautogui.press('r')
    await asyncio.sleep(1)
    pyautogui.press('q')
    pyautogui.keyUp('ctrl')


async def handle_user_message(message):
    """Validate and save the user-sent message to a file to be read by the Auto-Hotkey script"""
    if constants.MENTION_PATTERN.match(message.content) or constants.AHK_PATTERN.match(message.content):
        await message.channel.send(f'VALIDATION ERROR: {message.author.name}, your message was not sent.')
        return
    message.content = message.content.replace('\n', ' ').replace('\t', ' ')
    message.content = profanity.censor(message.content)
    name = message.author.name
    if message.author.nick:
        name = message.author.nick
    line = ("(" + name + "): " + message.content).encode("LATIN-1", "ignore").decode("UTF-8", "ignore")
    if line:
        try:
            channel = USER_CHANNEL_IDS[message.channel.id]
            LOG.info('[' + channel + ']: ' + line)
            file = open(channel + '_crosschat.txt', 'a+')
            file.write(line + '\n')
            file.close()
        except OSError:
            await message.channel.send(f'ERROR: {message.author.name}, your message was not sent.')


@slash.slash(name="restart", description="restarts crosschat", guild_ids=[int(settings.load()['discord']['guild_id'])])
@slash.permission(guild_id=int(settings.load()['discord']['guild_id']), permissions=[create_permission(int(settings.load()['discord']['admin_role']), SlashCommandPermissionType.ROLE, True)])
async def restart(context: SlashContext):
    await context.send("Restarting CROSSCHAT, standby...")
    await handle_restart()


@slash.slash(name="audit", description="run a member audit and show the report", guild_ids=[int(settings.load()['discord']['guild_id'])],
             options=[
                 create_option(name="autocorrect", description="automatically fix problems", option_type=SlashCommandOptionType.BOOLEAN, required=False)
             ])
@slash.permission(guild_id=int(settings.load()['discord']['guild_id']), permissions=[create_permission(int(settings.load()['discord']['admin_role']), SlashCommandPermissionType.ROLE, True)])
async def audit(context: SlashContext, autocorrect: bool = False):
    message = '**Audit Report:** \n'
    await context.send(message, delete_after=60)
    check_discord_members_for_name_in_note(context)
    check_members_for_name_match_and_permissions(context, autocorrect)


def check_discord_members_for_name_in_note(context):
    message = ''
    game_members = get_guild_members(False)
    for discord_member in context.guild.members:
        for role in discord_member.roles:
            if role.id == int(settings.load()['discord']['member_role']):
                is_member = False
                for game_member in game_members:
                    is_member = is_member_discord_member(game_member, discord_member)
                if not is_member:
                    message = message + '(<@' + str(discord_member.id) + '>) is not a guild member (set note or kick)\n'
    send_temp_message(context, message)


def is_member_discord_member(game_member, discord_member):
    if game_member.officernote == discord_member.__str__():
        return True


async def check_members_for_name_match_and_permissions(context, autocorrect):
    message = ''
    game_members = get_guild_members(False)
    for game_member in game_members:
        for discord_member in context.guild.members:
            if game_member.officernote == discord_member.__str__():
                is_member = False
                for role in discord_member.roles:
                    if role.id == int(settings.load()['discord']['member_role']):
                        is_member = True
                        if str.lower(game_member.name) not in str.lower(discord_member.display_name):
                            message = message + game_member.name + '(<@' + str(discord_member.id) + '>) character and discord name (' + discord_member.display_name + ') does not match (change nickname or move note)\n'
                if not is_member:
                    message = message + game_member.name + '(<@' + str(discord_member.id) + '>) does not have member permissions (grant or remove note)\n'
                    if autocorrect:
                        await discord_member.add_roles(context.guild.get_role(int(settings.load()['discord']['member_role'])))
    send_temp_message(context, message)


async def send_temp_message(context, message):
    if len(message) > 0:
        message = message[:constants.DISCORD_MESSAGE_LIMIT-3] + (message[constants.DISCORD_MESSAGE_LIMIT-3:] and '...')
        await context.send(message, delete_after=60)


@slash.slash(name="who", description="shows who is online in the guild", guild_ids=[int(settings.load()['discord']['guild_id'])],
             options=[
                 create_option(name="level", description="example: 60", option_type=SlashCommandOptionType.STRING, required=False),
                 create_option(name="name", description="example: Bonkeybee", option_type=SlashCommandOptionType.STRING, required=False)
             ])
@slash.permission(guild_id=int(settings.load()['discord']['guild_id']), permissions=[create_permission(int(settings.load()['discord']['member_role']), SlashCommandPermissionType.ROLE, True)])
async def who(context: SlashContext, level: str = None, name: str = None):
    if level or name:
        members = filter_members_by_name(name, filter_members_by_level(level, get_guild_members(False)))
        message = '**Found ' + str(members.__len__()) + ' matches:**\n'
        for member in members:
            message += member.__str__() + '\n'
        send_temp_message(context, message)
    else:
        members = get_guild_members()
        message = '**' + str(members.__len__()) + ' members online:**\n'
        for member in members:
            message += member.__simple__() + '\n'
        message = message[:constants.DISCORD_MESSAGE_LIMIT-3] + (message[constants.DISCORD_MESSAGE_LIMIT-3:] and '...')
        await context.send(message, delete_after=60)


def filter_members_by_level(level, members):
    if level:
        if '+' in level:
            level = int(''.join(filter(str.isdigit, level)))
            members = list(filter(lambda m: m.level >= level, members))
        elif '-' in level:
            level = int(''.join(filter(str.isdigit, level)))
            members = list(filter(lambda m: m.level <= level, members))
        else:
            level = int(''.join(filter(str.isdigit, level)))
            members = list(filter(lambda m: m.level == level, members))
    return members

def filter_members_by_name(name, members):
    if name:
        members = list(filter(lambda m: str.lower(name) in str.lower(m.name), members))
    return members


@bot.event
async def on_message(message):
    """Discord message handling"""
    if not message.author.bot and message.channel.id in USER_CHANNEL_IDS.keys():
        await handle_user_message(message)


guildchat = asyncio.get_event_loop().create_task(chat_log_to_discord_webhook('guild_chat_log_file', 'GUILDCHATLOG = {', 'guild', 'guild_chat_webhook_url', None, None, None, None, None))
officerchat = asyncio.get_event_loop().create_task(chat_log_to_discord_webhook('officer_chat_log_file', 'OFFICERCHATLOG = {', 'officer', 'officer_chat_webhook_url', None, None, None, None, None))
systemchat = asyncio.get_event_loop().create_task(chat_log_to_discord_webhook('system_chat_log_file', 'SYSTEMCHATLOG = {', 'system', 'system_chat_webhook_url', None, None, None, None, None))
lfgchat = asyncio.get_event_loop().create_task(chat_log_to_discord_webhook('lfg_chat_log_file', 'LFGCHATLOG = {', 'lfg', 'lfg_chat_webhook_url', 'LookingForGroup', 'lfg_crosschat_channel_id', 'lfg_embed_message_id', [constants.LAZY_LFG_PATTERN, constants.BOOST_PATTERN, constants.GUILD_PATTERN, constants.RECRUITING_PATTERN], [constants.LFG_PATTERN]))
discordbot = asyncio.get_event_loop().create_task(bot.run(settings.load()['discord']['token']))

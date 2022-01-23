"""Handles the discord<->game portion of crosschat"""
import asyncio
import atexit
import logging
import re
import time
from collections import OrderedDict
from http import HTTPStatus
from os import system
import os
import random
from boto3 import Session
from contextlib import closing

import discord
from discord import HTTPException
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord_slash.model import SlashCommandPermissionType, SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option, create_permission
from tendo import singleton

import settings
from lib.beans.message import Message
from lib.services.audit_service import check_discord_members_for_name_in_note, check_members_for_name_match_and_permissions
from lib.services.chat_log_service import parse_chat_log, load_chat_log
from lib.services.exception_service import send_exception
from lib.services.message_service import push_all, add_message, handle_user_message
from lib.services.restart_service import handle_restart
from lib.services.who_service import detailed_who, simple_who
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

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
slash = SlashCommand(bot, sync_commands=True)
voice_client = None
session = Session(profile_name="CrosschatPolly")
polly = session.client("polly")
greetings = ["Hello", "Greetings", "Hi", "Howdy", "Welcome", "Hey", "Hi-ya", "How are you", "How goes it", "Howdy-do", "What's happening", "What's up", "Uh-oh, it's"]
farewells = ["Goodbye", "Bye", "Bye-bye", "Godspeed", "So long", "Farewell", "See ya later"]


# noinspection PyBroadException
async def chat_log_to_discord_webhook(chat_log_file_option, starting_key, channel, webhook_url_option, embed_name, embed_channel_id_option, embed_message_id_option, bad_patterns, good_patterns):
    """Reads the World of Warcraft addon chat logs and pushes new messages to the Discord webhook and/or embed"""
    global voice_client
    while voice_client is None:
        await asyncio.sleep(0.1)
    try:
        await bot.wait_until_ready()
        while True:
            messages = get_chat_log_messages(chat_log_file_option, starting_key, channel)
            if embed_name and embed_channel_id_option and embed_message_id_option:
                messages = await handle_embed(messages, embed_name, embed_channel_id_option, embed_message_id_option, bad_patterns, good_patterns)
            if messages:
                push_all(settings.load()['discord'][webhook_url_option], messages, channel)
            if channel == "guild" and voice_client.is_connected():
                path = "sounds/text.mp3"
                for message in messages:
                    while voice_client.is_playing():
                        await asyncio.sleep(0.1)
                    speech = polly.synthesize_speech(Text=message.player + " says: " + message.raw, OutputFormat="mp3", VoiceId="Takumi", Engine="neural")
                    with closing(speech["AudioStream"]) as stream:
                        with open(path, "wb") as file:
                            file.write(stream.read())
                    await asyncio.sleep(0.1)
                    voice_client.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source=path))
            await asyncio.sleep(constants.CHAT_LOG_CYCLE_TIME)
    except Exception as e:
        await send_exception(e, bot)


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
        message.line = re.compile('\\b(tank|tanks)\\b', re.IGNORECASE).sub('<@&' + settings.load()['discord']['tank_role'] + '>', message.line)
        message.line = re.compile('\\b(heal|heals|healer)\\b', re.IGNORECASE).sub('<@&' + settings.load()['discord']['heal_role'] + '>', message.line)
        message.line = re.compile('\\b(dps)\\b', re.IGNORECASE).sub('<@&' + settings.load()['discord']['dps_role'] + '>', message.line)
        message.line = re.compile('\\b(all)\\b', re.IGNORECASE).sub('<@&' + settings.load()['discord']['tank_role'] + '><@&' + settings.load()['discord']['heal_role'] + '><@&' + settings.load()['discord']['dps_role'] + '>', message.line)
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
    global voice_client
    LOG.info(bot.user.name + ' has connected to Discord!')
    voice_client = await bot.get_channel(int(settings.load()['discord']['guild_general_voice_channel_id'])).connect()
    if not os.path.exists("sounds"):
        os.makedirs("sounds")


@bot.event
async def on_voice_state_update(member, before, after):
    global voice_client
    global greetings
    global farewells
    if voice_client is not None and voice_client.is_connected():
        channel = int(settings.load()['discord']['guild_general_voice_channel_id'])
        if (before.channel is None or before.channel.id != channel) and after.channel is not None and after.channel.id == channel:
            await ackknowledge_member("hello", member)
        if before.channel.id == channel and (after.channel is None or after.channel.id != channel):
            await ackknowledge_member("goodbye", member)


async def ackknowledge_member(type, member):
    global greetings
    global farewells
    name = member.nick
    if name is None:
        name = member.name
    if type == "hello":
        speech = polly.synthesize_speech(Text=random.choice(greetings) + " " + name + "!", OutputFormat="mp3", VoiceId="Takumi", Engine="neural")
    else:
        speech = polly.synthesize_speech(Text=random.choice(farewells) + " " + name + "!", OutputFormat="mp3", VoiceId="Takumi", Engine="neural")
    while voice_client.is_playing():
        await asyncio.sleep(0.1)
    with closing(speech["AudioStream"]) as stream:
        with open("sounds/"+type+".mp3", "wb") as file:
            file.write(stream.read())
    voice_client.play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source="sounds/" + type + ".mp3"))


@bot.event
async def on_message(message):
    """Discord message handling"""
    if not message.author.bot:
        await handle_user_message(message)


@slash.slash(name="restart", description="restarts crosschat", guild_ids=[int(settings.load()['discord']['guild_id'])])
@slash.permission(guild_id=int(settings.load()['discord']['guild_id']), permissions=[create_permission(int(settings.load()['discord']['admin_role']), SlashCommandPermissionType.ROLE, True)])
async def restart(context: SlashContext):
    """Restarts the CROSSCHAT service"""
    await context.send("Restarting CROSSCHAT, standby...")
    await handle_restart()


@slash.slash(name="audit", description="run a member audit and show the report", guild_ids=[int(settings.load()['discord']['guild_id'])])
@slash.permission(guild_id=int(settings.load()['discord']['guild_id']), permissions=[create_permission(int(settings.load()['discord']['admin_role']), SlashCommandPermissionType.ROLE, True)])
async def audit(context: SlashContext):
    """Generates an audit report which contains members with mismatched permissions or names"""
    await send_temp_message(context, '**Generating Audit Report:** \n')
    await send_temp_message(context, check_discord_members_for_name_in_note(context.guild.members))
    await send_temp_message(context, check_members_for_name_match_and_permissions(context.guild.members))
    await send_temp_message(context, '**Audit Report Complete**')


@slash.slash(name="who", description="shows who is online in the guild", guild_ids=[int(settings.load()['discord']['guild_id'])],
             options=[
                 create_option(name="level", description="example: 60", option_type=SlashCommandOptionType.STRING, required=False),
                 create_option(name="name", description="example: Bonkeybee", option_type=SlashCommandOptionType.STRING, required=False)
             ])
@slash.permission(guild_id=int(settings.load()['discord']['guild_id']), permissions=[create_permission(int(settings.load()['discord']['member_role']), SlashCommandPermissionType.ROLE, True)])
async def who(context: SlashContext, level: str = None, name: str = None):
    """Generates a who report which contains character data from the game"""
    if level or name:
        await send_temp_message(context, detailed_who(level, name))
    else:
        await send_temp_message(context, simple_who())


async def send_temp_message(context, message):
    """Sends a message to discord that auto-deletes after a minute"""
    if len(message) > 0:
        message = message[:constants.DISCORD_MESSAGE_LIMIT - 3] + (message[constants.DISCORD_MESSAGE_LIMIT - 3:] and '...')
        await context.send(message, delete_after=60)


async def on_close():
    await bot.close()


guildchat = asyncio.get_event_loop().create_task(chat_log_to_discord_webhook('guild_chat_log_file', 'GUILDCHATLOG = {', 'guild', 'guild_chat_webhook_url', None, None, None, None, None))
officerchat = asyncio.get_event_loop().create_task(chat_log_to_discord_webhook('officer_chat_log_file', 'OFFICERCHATLOG = {', 'officer', 'officer_chat_webhook_url', None, None, None, None, None))
systemchat = asyncio.get_event_loop().create_task(chat_log_to_discord_webhook('system_chat_log_file', 'SYSTEMCHATLOG = {', 'system', 'system_chat_webhook_url', None, None, None, None, None))
lfgchat = asyncio.get_event_loop().create_task(chat_log_to_discord_webhook('lfg_chat_log_file', 'LFGCHATLOG = {', 'lfg', 'lfg_chat_webhook_url', 'LookingForGroup', 'lfg_crosschat_channel_id', 'lfg_embed_message_id', [constants.LAZY_LFG_PATTERN, constants.BOOST_PATTERN, constants.GUILD_PATTERN, constants.RECRUITING_PATTERN], [constants.LFG_PATTERN]))
discordbot = asyncio.get_event_loop().create_task(bot.run(settings.load()['discord']['token']))
atexit.register(on_close)

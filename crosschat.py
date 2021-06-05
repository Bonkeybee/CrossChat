"""Handles the discord->game portion of crosschat"""
import asyncio
import logging
import re
import time
from collections import OrderedDict
from os import system

import discord
import pyautogui
from better_profanity import profanity
from discord import HTTPException
from discord.ext import commands
from tendo import singleton

import settings
from lib.beans.message import Message
from lib.services.chat_log_service import parse_chat_log, load_chat_log
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
bot = commands.Bot(command_prefix='!')

USER_CHANNEL_IDS = {int(settings.load()['discord']['guild_crosschat_channel_id']): 'guild', int(settings.load()['discord']['officer_crosschat_channel_id']): 'officer'}


async def chat_log_to_discord_webhook(chat_log_file_option, starting_key, channel, webhook_url_option, embed_name, embed_channel_id_option, embed_message_id_option, bad_patterns, good_patterns):
    """Reads the World of Warcraft addon chat logs and pushes new messages to the Discord webhook and/or embed"""
    await bot.wait_until_ready()
    while True:
        messages = get_chat_log_messages(chat_log_file_option, starting_key, channel)
        if embed_name and embed_channel_id_option and embed_message_id_option:
            messages = await handle_embed(messages, embed_name, embed_channel_id_option, embed_message_id_option, bad_patterns, good_patterns)
        if messages:
            push_all(settings.load()['discord'][webhook_url_option], messages, channel)
        await asyncio.sleep(6)


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
        if exception.code == 504 and attempts <= 5:
            await asyncio.sleep(pow(attempts + 1, 2))
            return await get_message_with_retry(channel_id, message_id, attempts + 1)


def get_old_messages_from_embed(discord_embed):
    """Parse the previously sent messages from the embed"""
    old_messages = []
    for field in discord_embed.fields:
        if field.name and field.value:
            timestamp = field.name.split(':')[0]
            player = field.name.split(':')[1].strip()
            line = ':'.join(field.value.split(':')[1:]).strip()
            if line:
                message = Message(timestamp, player, line)
                old_messages.append(message)
    return old_messages


def add_embed_fields(old_messages, embed):
    """Add messages to the embed fields"""
    for message in old_messages:

        message.line = re.compile('\\b(tank)\\b', re.IGNORECASE).sub('<@&588127212943704065>', message.line)
        message.line = re.compile('\\b(heals|healer)\\b', re.IGNORECASE).sub('<@&588127189434892288>', message.line)
        message.line = re.compile('\\b(dps)\\b', re.IGNORECASE).sub('<@&588127168098336768>', message.line)
        duration = int((float(time.time()) - float(message.timestamp)) / 60)
        if duration <= 60:
            readable_duration = str(duration) + ' minutes ago'
            if duration == 0:
                readable_duration = 'just now'
            if duration == 1:
                readable_duration = str(duration) + ' minute ago'
            embed.add_field(name=(message.timestamp + ':  ' + message.player), value=(readable_duration + ': ' + message.line), inline=True)


# DISCORD STUFF
@bot.event
async def on_ready():
    """Indicator for when the bot connects to discord"""
    LOG.info(bot.user.name + ' has connected to Discord!')


async def handle_restart():
    """Send a key-combination on the host to trigger the Auto-Hotkey script reload"""
    for key in USER_CHANNEL_IDS:
        await bot.get_channel(key).send('Restarting CROSSCHAT, standby...')
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


@bot.event
async def on_message(message):
    """Discord message handling"""
    if not message.author.bot:
        if message.author.id == int(settings.load()['discord']['admin_id']) and constants.RESTART_PATTERN.match(message.content):
            await handle_restart()
            return
        if message.channel.id in USER_CHANNEL_IDS.keys():
            await handle_user_message(message)


# noinspection PyBroadException
try:
    guildchat = asyncio.get_event_loop().create_task(chat_log_to_discord_webhook('guild_chat_log_file', 'GUILDCHATLOG = {', 'guild', 'guild_chat_webhook_url', None, None, None, None, None))
    officerchat = asyncio.get_event_loop().create_task(chat_log_to_discord_webhook('officer_chat_log_file', 'OFFICERCHATLOG = {', 'officer', 'officer_chat_webhook_url', None, None, None, None, None))
    systemchat = asyncio.get_event_loop().create_task(chat_log_to_discord_webhook('system_chat_log_file', 'SYSTEMCHATLOG = {', 'system', 'system_chat_webhook_url', None, None, None, None, None))
    lfgchat = asyncio.get_event_loop().create_task(chat_log_to_discord_webhook('lfg_chat_log_file', 'LFGCHATLOG = {', 'lfg', 'lfg_chat_webhook_url', 'LookingForGroup', 'lfg_crosschat_channel_id', 'lfg_embed_message_id', [constants.LAZY_LFG_PATTERN, constants.BOOST_PATTERN, constants.GUILD_PATTERN], [constants.LFG_PATTERN]))
    discordbot = asyncio.get_event_loop().create_task(bot.run(settings.load()['discord']['token']))
except Exception as e:
    LOG.exception('Unexpected exception')

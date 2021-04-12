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


async def chat_log_to_discord_webhook(chat_log_file_option, starting_key, channel, webhook_url_option):
    await bot.wait_until_ready()
    while True:
        messages = []
        chat_log = load_chat_log(settings.load()['wow'][chat_log_file_option])
        chat_log_length = len(chat_log)
        data_start = None
        for index, line in enumerate(chat_log):
            if index < chat_log_length - 1:
                if re.match(starting_key, chat_log[index]):
                    data_start = index + 1
                if data_start is not None and ((index + data_start) % 4) == 0:
                    timestamp, player, message = parse_chat_log(index, chat_log)
                    add_message(messages, timestamp, player, message, channel)
        messages.sort()
        push_all(settings.load()['discord'][webhook_url_option], messages, channel)
        await asyncio.sleep(1)


async def looking_for_group_to_discord_webhook():
    await bot.wait_until_ready()
    while True:
        messages = []
        chat_log = load_chat_log(settings.load()['wow']['lfg_chat_log_file'])
        chat_log_length = len(chat_log)
        data_start = None
        for index, line in enumerate(chat_log):
            if index < chat_log_length - 1:
                if re.match('LFGCHATLOG = {', chat_log[index]):
                    data_start = index + 1
                if data_start is not None and ((index + data_start) % 4) == 0:
                    timestamp, player, message = parse_chat_log(index, chat_log)
                    add_message(messages, timestamp, player, message, 'lfg')
        messages.sort()
        messages = await update_lfg(messages)
        if messages:
            push_all(settings.load()['discord']['lfg_chat_webhook_url'], messages, 'lfg')
        await asyncio.sleep(1)


async def update_lfg(messages: list[Message]) -> list[Message]:
    if messages:
        if settings.load().has_section('state') and settings.load().has_option('state', 'lfg_embed_message_id'):
            discord_message: discord.Message = await bot.get_channel(int(settings.load()['discord']['lfg_crosschat_channel_id'])).fetch_message(int(settings.load()['state']['lfg_embed_message_id']))
            if not discord_message.embeds:
                return await create_lfg_embed(discord_message, [], messages)
            old_messages = []
            for field in discord_message.embeds[0].fields:
                if field.name and field.value:
                    timestamp = field.name.split(':')[0]
                    player = field.name.encode("LATIN-1", "ignore").decode("UTF-8", "ignore").split(':')[1].strip()
                    line = field.value.encode("LATIN-1", "ignore").decode("UTF-8", "ignore").partition(':')[1].strip()
                    message = Message(timestamp, player, line)
                    old_messages.append(message)
            old_messages.sort()
            return await create_lfg_embed(discord_message, old_messages, messages)
        else:
            return await create_lfg_embed(None, [], messages)
    else:
        await update_lfg_embed()


async def update_lfg_embed():
    if settings.load().has_section('state') and settings.load().has_option('state', 'lfg_embed_message_id'):
        discord_message: discord.Message = await bot.get_channel(int(settings.load()['discord']['lfg_crosschat_channel_id'])).fetch_message(int(settings.load()['state']['lfg_embed_message_id']))
        if not discord_message or not discord_message.embeds:
            return
        old_messages = []
        for field in discord_message.embeds[0].fields:
            if field.name and field.value:
                timestamp = field.name.split(':')[0]
                player = field.name.encode("LATIN-1", "ignore").decode("UTF-8", "ignore").split(':')[1].strip()
                line = field.value.encode("LATIN-1", "ignore").decode("UTF-8", "ignore").partition(':')[1].strip()
                message = Message(timestamp, player, line)
                old_messages.append(message)
        old_messages.sort(reverse=True)
        embed = discord.Embed(title=discord_message.embeds[0].title, description=discord_message.embeds[0].description)
        for message in old_messages:
            duration = int((float(time.time()) - float(message.timestamp)) / 60)
            if duration <= 60:
                readable_duration = str(duration) + ' minutes ago'
                if duration == 0:
                    readable_duration = 'just now'
                if duration == 1:
                    readable_duration = str(duration) + ' minute ago'
                embed.add_field(name=(message.timestamp + ':  ' + message.player), value=(readable_duration + ': ' + message.line), inline=False)
        await discord_message.edit(embed=embed)


async def create_lfg_embed(discord_message, old_messages, new_messages):
    lfg_messages = []
    non_lfg_messages = []
    for message in new_messages:
        if constants.BOOST_PATTERN.match(message.line):
            continue
        if constants.LFG_PATTERN.match(message.line):
            lfg_messages.append(message)
        else:
            non_lfg_messages.append(message)
    embed = discord.Embed(title='LookingForGroup', description=new_messages[-1].timestamp)
    messages_to_embed = old_messages + lfg_messages
    messages_to_embed = list(OrderedDict.fromkeys(messages_to_embed))
    messages_to_embed.sort()
    message_map = {}
    for message in messages_to_embed:
        message_map[message.player] = message
    messages_to_embed = list(message_map.values())
    messages_to_embed.sort(reverse=True)
    for message in messages_to_embed:
        duration = int((float(time.time()) - float(message.timestamp)) / 60)
        if duration <= 60:
            readable_duration = str(duration) + ' minutes ago'
            if duration == 0:
                readable_duration = 'just now'
            if duration == 1:
                readable_duration = str(duration) + ' minute ago'
            embed.add_field(name=(message.timestamp + ':  ' + message.player), value=(readable_duration + ': ' + message.line), inline=False)
    if discord_message:
        await discord_message.edit(embed=embed)
    else:
        discord_message = await bot.get_channel(int(settings.load()['discord']['lfg_crosschat_channel_id'])).send(embed=embed)
        settings.load()['state']['lfg_embed_message_id'] = str(discord_message.id)
        with open(constants.CONFIG_FILE, 'w') as configfile:
            settings.load().write(configfile)
    return non_lfg_messages


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
    asyncio.get_event_loop().create_task(chat_log_to_discord_webhook('guild_chat_log_file', 'GUILDCHATLOG = {', 'guild', 'guild_chat_webhook_url'))
    asyncio.get_event_loop().create_task(chat_log_to_discord_webhook('officer_chat_log_file', 'OFFICERCHATLOG = {', 'officer', 'officer_chat_webhook_url'))
    asyncio.get_event_loop().create_task(chat_log_to_discord_webhook('system_chat_log_file', 'SYSTEMCHATLOG = {', 'system', 'system_chat_webhook_url'))
    asyncio.get_event_loop().create_task(looking_for_group_to_discord_webhook())
    asyncio.get_event_loop().create_task(bot.run(settings.load()['discord']['token']))
except Exception as e:
    LOG.exception('Unexpected exception')

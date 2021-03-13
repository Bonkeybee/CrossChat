"""Handles the discord->game portion of crosschat"""
import logging
import os
import re
import threading
import time
from os import system

import pyautogui
from better_profanity import profanity
from discord.ext import commands
from tendo import singleton

from lib.services.chat_log_service import parse_chat_log, load_chat_log
from lib.services.config_service import load_config
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

config, debug = load_config(os.getcwd())

CHANNEL_IDS = {int(config['discord']['guild_crosschat_channel_id']): 'guild', int(config['discord']['officer_crosschat_channel_id']): 'officer'}


def chat_log_to_discord_webhook(chat_log_file_option, starting_key, channel, webhook_url_option):
    while True:
        messages = []
        chat_log = load_chat_log(config['wow'][chat_log_file_option])
        chat_log_length = len(chat_log)
        data_start = None
        for index, line in enumerate(chat_log):
            if index < chat_log_length - 1:
                if re.match(starting_key, chat_log[index]):
                    data_start = index + 1
                if data_start is not None and ((index + data_start) % 4) == 0:
                    timestamp, player, message = parse_chat_log(index, chat_log)
                    add_message(messages, timestamp, player, message, channel, config)
        messages.sort()
        push_all(config['discord'][webhook_url_option], messages, channel, config)
        time.sleep(1)


# DISCORD STUFF
@bot.event
async def on_ready():
    """Indicator for when the bot connects to discord"""
    LOG.info(bot.user.name + ' has connected to Discord!')
    for key in CHANNEL_IDS:
        await bot.get_channel(key).send('CROSSCHAT connected.')


async def handle_restart(message):
    """Send a key-combination on the host to trigger the Auto-Hotkey script reload"""
    for key in CHANNEL_IDS:
        await bot.get_channel(key).send('Restarting CROSSCHAT, standby...')
    pyautogui.keyDown('ctrl')
    pyautogui.press('r')
    time.sleep(1)
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
            channel = CHANNEL_IDS[message.channel.id]
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
        if message.author.id == int(config['discord']['admin_id']) and constants.RESTART_PATTERN.match(message.content):
            await handle_restart(message)
            return
        if message.channel.id == int(config['discord']['crosschat_channel_id']):
            await handle_user_message(message)


# noinspection PyBroadException
try:
    discord_bot = threading.Thread(target=bot.run, args=(config['discord']['token'],), daemon=True)
    discord_bot.start()
    guild_chat = threading.Thread(target=chat_log_to_discord_webhook, args=('guild_chat_log_file', 'GUILDCHATLOG = {', 'guild', 'guild_chat_webhook_url',), daemon=True)
    guild_chat.start()
    officer_chat = threading.Thread(target=chat_log_to_discord_webhook, args=('officer_chat_log_file', 'OFFICERCHATLOG = {', 'officer', 'officer_chat_webhook_url',), daemon=True)
    officer_chat.start()

    discord_bot.join()
    guild_chat.join()
    officer_chat.join()
except Exception as e:
    LOG.exception('Unexpected exception')

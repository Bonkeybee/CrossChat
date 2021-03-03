################################### IMPORTS ####################################
from os import system
system('title ' + 'crosschat-discord')

from tendo import singleton
me = singleton.SingleInstance()

import logging
logging.basicConfig(filename='errors.log', level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s')
LOG=logging.getLogger(__name__)

import configparser
config = configparser.ConfigParser()
config.read('config.ini')
TOKEN = config['discord']['TOKEN']
ADMIN_ID = int(config['discord']['ADMIN_ID'])
LOG_CHANNEL_ID = int(config['discord']['LOG_CHANNEL_ID'])
CROSSCHAT_CHANNEL_ID = int(config['discord']['CROSSCHAT_CHANNEL_ID'])

import discord
from discord.ext import commands
bot = commands.Bot(command_prefix='!')

import re
MENTION_PATTERN = re.compile('<@.+>')
AHK_PATTERN = re.compile('{.*}')
RESTART_PATTERN = re.compile('!restart')

import spacy
from profanity_filter import ProfanityFilter
pf = ProfanityFilter()

import pyautogui
import time

################################### GLOBALS ####################################

################################## FUNCTIONS ###################################
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    channel = bot.get_channel(CROSSCHAT_CHANNEL_ID)
    await channel.send(f'CROSS-CHAT connected.')

@bot.event
async def on_message(message):
    if message.author.bot == False:
        if message.channel.id == CROSSCHAT_CHANNEL_ID:
            if MENTION_PATTERN.match(message.content) or AHK_PATTERN.match(message.content):
                await message.channel.send(f'VALIDATION ERROR: {message.author.name}, your message was not sent.')
                return
            message.content = message.content.replace('\n', ' ').replace('\t', ' ')
            message.content = pf.censor(message.content)
            name = message.author.name
            if message.author.nick:
                name = message.author.nick
            line = ("("+name+"): "+message.content).encode("LATIN-1", "ignore").decode("UTF-8", "ignore")
            if line:
                try:
                    print('sent: ' + line)
                    fout = open('crosschat.txt', 'a+')
                    fout.write(line + '\n')
                except:
                    await message.channel.send(f'ERROR: {message.author.name}, your message was not sent.')

        if message.author.id == ADMIN_ID and RESTART_PATTERN.match(message.content):
            await message.channel.send(f'Restarting CROSS-CHAT, standby...')
            pyautogui.keyDown('ctrl')
            pyautogui.press('r')
            time.sleep(1)
            pyautogui.press('q')
            pyautogui.keyUp('ctrl')

##################################### MAIN #####################################
bot.run(TOKEN)

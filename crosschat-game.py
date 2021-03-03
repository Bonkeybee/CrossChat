################################### IMPORTS ####################################
from os import system
system('title ' + 'crosschat-game')

from tendo import singleton
me = singleton.SingleInstance()

import configparser
config = configparser.ConfigParser()
config.read('config.ini')
CHATLOG_FILE = config['wow']['CHATLOG_FILE']
WEBHOOK_URL = config['discord']['WEBHOOK_URL']

from contextlib import suppress
from datetime import datetime
import json
import operator
import requests
import re
import time
import os

import logging
logging.basicConfig(filename='errors.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(message)s')
LOG=logging.getLogger(__name__)

################################### GLOBALS ####################################
TIMESTAMP_FILE = 'lastTimestamp.txt'
lastTimestamp = 0

ITEM_REPLACE_REGEX = '\|(.+Hitem:([0-9]+).+)\|r'
ITEM_PATTERN = re.compile('.*' + ITEM_REPLACE_REGEX + '.*')
WOWHEAD_ITEM_URL = 'https://classic.wowhead.com/item='

################################## FUNCTIONS ###################################
class Message:
    def __init__(self, timestamp, player, message):
        self.timestamp = timestamp
        self.player = player
        self.message = message
    def __lt__(self, other):
        return self.timestamp < other.timestamp
    def toString(self):
        readableTimestamp = time.strftime('%I:%M:%S %p', time.gmtime(float(self.timestamp)-18000))
        return ("`["+readableTimestamp+"]` ["+self.player+"]: "+self.message).encode("LATIN-1", "ignore").decode("UTF-8", "ignore")

def initialize():
    global lastTimestamp
    with suppress(Exception):
        initializationFile = open(TIMESTAMP_FILE, 'r')
        lastTimestamp = float(initializationFile.read())

def saveState():
    global lastTimestamp
    fout = open(TIMESTAMP_FILE, 'w')
    fout.write(str(lastTimestamp))

def escapeSequences(message):
    if '*' in message:
        print('### mutating: ' + message)
        message = message.replace('*', '\*')
    return message

def replaceItemPatterns(message):
    if ITEM_PATTERN.match(message):
        print('### mutating: ' + message)
        splitMessage = message.split('|r')
        message = ''
        for split in splitMessage:
            splitMatch = ITEM_PATTERN.match(split + '|r')
            if splitMatch:
                id = splitMatch.group(2)
                split = re.sub(ITEM_REPLACE_REGEX, WOWHEAD_ITEM_URL + id, split + '|r')
                message = message + split + ' '
            else:
                message = message + split
    return message

def scrubMessage(message):
    return replaceItemPatterns(escapeSequences(message))

def parseChatlog(index, chatlog):
    timestamp = chatlog[index].split('[')[1].split(']')[0]
    player = chatlog[index + 1].split('"')[1]
    message = chatlog[index + 2].replace('\\"', '\'').split('"')[1]
    return timestamp, player, message

def isNewMessage(message):
    global lastTimestamp
    if lastTimestamp < float(message.timestamp):
        return True
    return False

def doesNotContainMentions(message):
    if message.message.find('@everyone') == -1 and message.message.find('@here') == -1:
        return True
    return False

def addMessage(messages, timestamp, player, message):
    global lastTimestamp
    message = Message(timestamp, player, message)
    if isNewMessage(message) and doesNotContainMentions(message):
        message.message = scrubMessage(message.message)
        messages.append(message)

def bulkify(i, j, messages):
    bulkMessage = ''
    for index in range(i, j):
        bulkMessage = bulkMessage + messages[index].toString() + '\n'
    return bulkMessage

def push(timestamp, content):
    global lastTimestamp
    status = 0
    while status == 0 or status == 429:
        response = requests.post(url = WEBHOOK_URL, data = {'content':content})
        status = response.status_code
        if status == 429:
            print('waiting for request limit...')
            time.sleep(1)
    lastTimestamp = timestamp
    print(content)

def pushAll(messages):
    messagesLength = len(messages)
    bulkIndex = 0
    while messagesLength > 0 and bulkIndex < messagesLength:
        maxIndex = min(bulkIndex + 6, messagesLength)
        bulkMessage = bulkify(bulkIndex, maxIndex, messages)
        bulkIndex = maxIndex
        push(float(messages[bulkIndex-1].timestamp), bulkMessage)
        saveState()

def loadChatlog():
    chatlog = None
    while chatlog is None:
        try:
            with open(CHATLOG_FILE, mode='r', encoding='LATIN-1') as chatlogFile:
                chatlog = chatlogFile.readlines()
        except Exception as e:
            LOG.error(e)
            time.sleep(1)
            pass
    return chatlog

##################################### MAIN #####################################
try:
    initialize()
    while True:
        messages = []
        chatlog = loadChatlog()
        chatlogLength = len(chatlog)
        dataStart = None
        for index, line in enumerate(chatlog):
            if index < chatlogLength - 1:
                if re.match(r"GUILDCHATLOG = {", chatlog[index]):
                    dataStart = index + 1
                if dataStart != None and ((index + dataStart) % 4) == 0:
                    timestamp, player, message = parseChatlog(index, chatlog)
                    addMessage(messages, timestamp, player, message)
        messages.sort()
        pushAll(messages)
        time.sleep(1)
except Exception as e:
    LOG.error(e)

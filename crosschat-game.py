from os import system
system('title ' + 'crosschat-game')

from tendo import singleton
me = singleton.SingleInstance()

import configparser
config = configparser.ConfigParser()
config.read('config.ini')

from contextlib import suppress
from datetime import datetime
import json
import operator
import requests
import re
import time
import os

################################### GLOBALS ####################################

CHATLOG_FILE = config['wow']['CHATLOG_FILE']
TIMESTAMP_FILE = 'lastTimestamp.txt'

WEBHOOK_URL = config['discord']['WEBHOOK_URL']

ITEM_REPLACE_REGEX = '\|(.+Hitem:([0-9]+).+)\|r'
ITEM_REGEX = '.*' + ITEM_REPLACE_REGEX + '.*'
ITEM_PATTERN = re.compile(ITEM_REGEX)
WOWHEAD_ITEM_URL = 'https://classic.wowhead.com/item='

lastTimestamp = 0

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
        return ("["+readableTimestamp+"] ["+self.player+"]: "+self.message).encode("LATIN-1", "ignore").decode("UTF-8")


def initialize():
    global lastTimestamp
    with suppress(Exception):
        initializationFile = open(TIMESTAMP_FILE, 'r')
        lastTimestamp = float(initializationFile.read())

def saveState():
    global lastTimestamp
    fout = open(TIMESTAMP_FILE, 'w')
    fout.write(str(lastTimestamp))

def replaceItemPattern(message):
    match = ITEM_PATTERN.match(message)
    if match:
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
        message.message = replaceItemPattern(message.message)
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
            with open(CHATLOG_FILE, 'r') as chatlogFile:
                chatlog = chatlogFile.readlines()
        except:
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
    print(e)
    fout = open(datetime.now().strftime("%d-%m-%Y-%H-%M-%S.txt"), 'w')
    fout.write(str(e))

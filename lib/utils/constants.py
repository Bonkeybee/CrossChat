import re

MENTION_PATTERN = re.compile('<@.+>')
AHK_PATTERN = re.compile('{.*}')
RESTART_PATTERN = re.compile('!restart')

ITEM_REPLACE_REGEX = '\|(.+Hitem:([0-9]+).+)\|r'
ITEM_PATTERN = re.compile('.*' + ITEM_REPLACE_REGEX + '.*')

WOWHEAD_ITEM_URL = 'https://classic.wowhead.com/item='
TIMESTAMP_FILE = 'lastTimestamp.txt'

CONFIG_FILE = 'config\config.ini'
SAMPLE_CONFIG_FILE = 'config\config.sample'

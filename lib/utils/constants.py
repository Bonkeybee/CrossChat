import re

MENTION_PATTERN = re.compile('<@.+>')
AHK_PATTERN = re.compile('{.*}')
RESTART_PATTERN = re.compile('!restart')

ITEM_REPLACE_REGEX = '\|(.+Hitem:([0-9]+).+)\|r'
ITEM_PATTERN = re.compile('.*' + ITEM_REPLACE_REGEX + '.*')

ENCHANT_REPLACE_REGEX = '\|(.+Henchant:([0-9]+).+)\|r'
ENCHANT_PATTERN = re.compile('.*' + ENCHANT_REPLACE_REGEX + '.*')

LFG_PATTERN = re.compile('.*(lf|lfm|lfg|looking|any|anyone|need|tank[s]|heal[s]|dps).*( [/]*(tank[s]|heal[s]|healer[s]|dps|pvp|mara|zg|zf|ubrs|aq|aq20|aq40|st|brd|sfk|sm|dm|deadmine[s]|stockade[s]|stock[s]|gnomer|gnomeregan|strat|scholo|scholomance|dungeon)\\b).*', re.IGNORECASE)

SKULL = '{skull}'
CROSS = '{cross}'
SQUARE = '{square}'
MOON = '{moon}'
TRIANGLE = '{triangle}'
DIAMOND = '{diamond}'
CIRCLE = '{circle}'
STAR = '{star}'

WOWHEAD_ITEM_URL = 'https://classic.wowhead.com/item='
WOWHEAD_SPELL_URL = 'https://classic.wowhead.com/spell='
TIMESTAMP_FILE = 'lastTimestamp.txt'

CONFIG_FILE = 'config\config.ini'
SAMPLE_CONFIG_FILE = 'config\config.sample'

BACK_SLASH = '\\'
ADDONS = 'addons'
GUILDCHATLOGGER_ADDON = 'GuildChatLogger'
OFFICERCHATLOGGER_ADDON = 'OfficerChatLogger'
SYSTEMCHATLOGGER_ADDON = 'SystemChatLogger'
LFGCHATLOGGER_ADDON = 'LFGChatLogger'


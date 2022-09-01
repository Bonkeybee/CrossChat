"""Defines several constants to be used by the project"""
import re


MENTION_PATTERN = re.compile('<@.+>')
AHK_PATTERN = re.compile('{.*}')
RESTART_PATTERN = re.compile('!restart')

ITEM_REPLACE_REGEX = '\|(.+Hitem:([0-9]+).+)\|r'
ITEM_PATTERN = re.compile('.*' + ITEM_REPLACE_REGEX + '.*')
ITEM_PHONETIC_REPLACE_REGEX = '\|(.+Hitem:[0-9]+.+\[([a-zA-Z0-9\/\',\:\-\. ]+)\].+)\|r'
ITEM_PHONETIC_PATTERN = re.compile('.*' + ITEM_PHONETIC_REPLACE_REGEX + '.*')

ENCHANT_REPLACE_REGEX = '\|(.+Henchant:([0-9]+).+)\|r'
ENCHANT_PATTERN = re.compile('.*' + ENCHANT_REPLACE_REGEX + '.*')
ENCHANT_PHONETIC_REPLACE_REGEX = '\|(.+Henchant:[0-9]+.+\[([a-zA-Z0-9\/\',\:\-\. ]+)\].+)\|r'
ENCHANT_PHONETIC_PATTERN = re.compile('.*' + ENCHANT_PHONETIC_REPLACE_REGEX + '.*')

SPELL_REPLACE_REGEX = '\|(.+Hspell:([0-9]+).+)\|r'
SPELL_PATTERN = re.compile('.*' + SPELL_REPLACE_REGEX + '.*')
SPELL_PHONETIC_REPLACE_REGEX = '\|(.+Hspell:[0-9]+.+\[([a-zA-Z0-9\/\',\:\-\. ]+)\].+)\|r'
SPELL_PHONETIC_PATTERN = re.compile('.*' + SPELL_PHONETIC_REPLACE_REGEX + '.*')

TALENT_REPLACE_REGEX = '\|(.+Htalent:[0-9]+.+(\[([a-zA-Z0-9\/\',\:\-\. ]+)\]).+)\|r'
TALENT_PATTERN = re.compile('.*' + TALENT_REPLACE_REGEX + '.*')
TALENT_PHONETIC_REPLACE_REGEX = '\|(.+Htalent:[0-9]+.+\[([a-zA-Z0-9\/\',\:\-\. ]+)\].+)\|r'
TALENT_PHONETIC_PATTERN = re.compile('.*' + TALENT_PHONETIC_REPLACE_REGEX + '.*')

ACHIEVEMENT_REPLACE_REGEX = '\|(.+Hachievement:[0-9]+.+(\[([a-zA-Z0-9\/\',\:\-\. ]+)\]).+)\|r'
ACHIEVEMENT_PATTERN = re.compile('.*' + ACHIEVEMENT_REPLACE_REGEX + '.*')
ACHIEVEMENT_PHONETIC_REPLACE_REGEX = '\|(.+Hachievement:[0-9]+.+\[([a-zA-Z0-9\/\',\:\-\. ]+)\].+)\|r'
ACHIEVEMENT_PHONETIC_PATTERN = re.compile('.*' + ACHIEVEMENT_PHONETIC_REPLACE_REGEX + '.*')

PROFESSION_REPLACE_REGEX = '\|(.+Htrade:.+(\[([a-zA-Z0-9\/\',\:\-\. ]+)\]).+)\|r'
PROFESSION_PATTERN = re.compile('.*' + PROFESSION_REPLACE_REGEX + '.*')
PROFESSION_PHONETIC_REPLACE_REGEX = '\|(.+Htrade:[0-9]+.+\[([a-zA-Z0-9\/\',\:\-\. ]+)\].+)\|r'
PROFESSION_PHONETIC_PATTERN = re.compile('.*' + PROFESSION_PHONETIC_REPLACE_REGEX + '.*')


def group(regex):
    """Wraps the regex as a group"""
    return '(' + regex + ')'


def word(regex):
    """Wraps the regex as a word"""
    return '\\b' + regex + '\\b'


ANY = '*'
EXIST = '+'
OR = '|'
ANYTHING = '.' + ANY
SPACE = ' '
SLASH = '/'
LB = '\['
RB = '\]'
LC = '<'
RC = '>'
LETTER = '[a-z ]'
LETTERS = LETTER + EXIST
EMOJI_REGEX = group(':' + LETTERS + ':')
LOOKING_FOR_GROUP_REGEX = group('lfg')
LOOKING_REGEX = group('lf[1-9 ]*|lf[1-9 ]*m|lfm[1-9 ]*|looking|need')
ROLE_CLASS_REGEX = group('tanks*|heals*|healers*|dps|druid|hunter|mage|paladin|priest|rogue|shaman|warlock|warrior')
ANYTHING_REGEX = group('whatever|any|quest')
PVP_REGEX = group('pvp|arena|battlegrounds*')
DUNGEON_REGEX_VANILLA = 'rfc|wc|vc|dm|deadmines*|sfk|bfd|blackfathom|depths|stockades*|stocks*|gnomer|gnomeregan|rfk|sm|scarlet|monastery|rfd|razorfen|downs|uld|ulda|uldaman|zf|zulfarrak|zul|farrak|mara|maraudon|princess|st|sunken|temple|brd|lbrs|ubrs|dme|dmw|dmn|dire|diremaul|scholo|scolo|scholomance|strat|strath|stratholme|dungeon'
RAID_REGEX_VANILLA = 'mc|molten|ony|onyxia|onyxia lair|zg|zul|gurub|bwl|blackwing|aq|ahn\'qirah|aq20|aq40|naxx|naxxramas|raid'
DUNGEON_REGEX_TBC = 'hr|hfr|ramps*|ramparts*|bf|blood|furnace|sh|shattered|halls*|citadel|sp|slave|pens*|slavepens*|ub|underbog|sv|steamvaults*|steam vaults*|cfr|mt|mana|tombs*|ac|crypts*|seth|sethekk*|halls*|sl|shadow|labs*|shadowlabs*|slabs*|bm|black|morass|blackmorass|oh|ohb|dh|dk|ohf|durn|old|hillsbrad|foothills*|arc|arcatraz|bot|botanica|mech|mechanar|mgt|mrt|magisters*|terrace'
RAID_REGEX_TBC = 'kara|karazhan|gruul|gruuls|gruul\'s*|mag|matheridons|magtheridon\'s*|za|zulaman|zul\'aman|ssc|tk|bt|hyjal'
DUNGEON_REGEX = group(DUNGEON_REGEX_VANILLA + OR + RAID_REGEX_VANILLA + OR + DUNGEON_REGEX_TBC + OR + RAID_REGEX_TBC)
BOOST_REGEX = group('wtb|wts|boosts*|gdkp')
RECRUIT_REGEX = group('recruit|recruiting')
LOOKING_FOR = group(
    group(word(LOOKING_REGEX)) + EXIST + OR +
    group(word(ROLE_CLASS_REGEX)) + EXIST
)
ACTIVITY = group(
    SLASH + ANY +
    group(word(ANYTHING_REGEX) + OR + word(PVP_REGEX) + OR + word(DUNGEON_REGEX))
    + SLASH + ANY
)
LFG_PATTERN = re.compile(ANYTHING + word(
    group(
        LOOKING_FOR + ANYTHING + SPACE + ACTIVITY + OR +
        ACTIVITY + ANYTHING + SPACE + LOOKING_FOR
    )) + ANYTHING, re.IGNORECASE)
LAZY_LFG_PATTERN = re.compile(ANYTHING + word(LOOKING_FOR_GROUP_REGEX) + ANYTHING, re.IGNORECASE)
BOOST_PATTERN = re.compile(ANYTHING + word(BOOST_REGEX) + ANYTHING, re.IGNORECASE)
GUILD_PATTERN = re.compile(ANYTHING +
                           group(
                               group(LB + EMOJI_REGEX + ANY + LETTERS + EMOJI_REGEX + ANY + RB) + OR +
                               group(LC + EMOJI_REGEX + ANY + LETTERS + EMOJI_REGEX + ANY + RC)
                           ) + ANYTHING, re.IGNORECASE)
RECRUITING_PATTERN = re.compile(ANYTHING + word(RECRUIT_REGEX) + ANYTHING, re.IGNORECASE)
print('LFG_PATTERN:  ' + LFG_PATTERN.pattern)
print('BOOST_PATTERN:  ' + BOOST_PATTERN.pattern)
print('GUILD_PATTERN:  ' + GUILD_PATTERN.pattern)

SKULL = '{skull}'
CROSS = '{cross}'
SQUARE = '{square}'
MOON = '{moon}'
TRIANGLE = '{triangle}'
DIAMOND = '{diamond}'
CIRCLE = '{circle}'
STAR = '{star}'
RAIDMARKS = {'skull': SKULL, 'cross': CROSS, 'square': SQUARE, 'moon': MOON, 'triangle': TRIANGLE, 'diamond': DIAMOND, 'circle': CIRCLE, 'star': STAR}

WOWHEAD_ITEM_URL = 'https://wowhead.com/wotlk/item='
WOWHEAD_SPELL_URL = 'https://wowhead.com/wotlk/spell='
TIMESTAMP_FILE = 'lastTimestamp.txt'

CONFIG_FILE = 'config\config.ini'
SAMPLE_CONFIG_FILE = 'config\config.sample'

BACK_SLASH = '\\'
ADDONS = 'addons'
GUILDCHATLOGGER_ADDON = BACK_SLASH + 'GuildChatLogger'
OFFICERCHATLOGGER_ADDON = BACK_SLASH + 'OfficerChatLogger'
SYSTEMCHATLOGGER_ADDON = BACK_SLASH + 'SystemChatLogger'
LFGCHATLOGGER_ADDON = BACK_SLASH + 'LFGChatLogger'
GUILDINFO_ADDON = BACK_SLASH + 'GuildInfo'

CHAT_LOG_CYCLE_TIME = 6
DISCORD_EMBED_LIMIT = 6000
DISCORD_MESSAGE_LIMIT = 2000
DISCORD_RETRY_LIMIT = 3

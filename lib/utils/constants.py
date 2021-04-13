import re

MENTION_PATTERN = re.compile('<@.+>')
AHK_PATTERN = re.compile('{.*}')
RESTART_PATTERN = re.compile('!restart')

ITEM_REPLACE_REGEX = '\|(.+Hitem:([0-9]+).+)\|r'
ITEM_PATTERN = re.compile('.*' + ITEM_REPLACE_REGEX + '.*')

ENCHANT_REPLACE_REGEX = '\|(.+Henchant:([0-9]+).+)\|r'
ENCHANT_PATTERN = re.compile('.*' + ENCHANT_REPLACE_REGEX + '.*')


def group(regex):
    return '(' + regex + ')'


WORD = '\\b'
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
LETTER = '[a-z]'
LETTERS = LETTER + EXIST
EMOJI_REGEX = group(':' + LETTERS + ':')
LOOKING_REGEX = group('lf|lfm|lfg|looking|any|anyone|need')
ROLE_CLASS_REGEX = group('tanks*|heals*|healers*|dps|druid|hunter|mage|paladin|priest|rogue|shaman|warlock|warrior')
ANYTHING_REGEX = group('whatever|any|work|quest')
PVP_REGEX = group('pvp|arena|battlegrounds*')
DUNGEON_REGEX = group('rfc|wc|dm|deadmines*|sfk|bfd|stockades*|stocks*|gnomer|gnomeregan|rfk|sm|rfd|uld|ulda|uldaman|zf|mara|maraudon|st|brd|lbrs|ubrs|dme|dmw|dmn|dire|diremaul|scholo|scholomance|strat|mc|ony|zg|bwl|aq|aq20|aq40|naxx|dungeon')
BOOST_REGEX = group('wtb|wts|boosts*|gdkp')
#LFG_PATTERN = re.compile('.*\\b(lf|lfm|lfg|looking|any|anyone|need|tank[s]*|heal[s]*|healer[s]*|dps|druid|hunter|mage|paladin|priest|rogue|shaman|warlock|warrior).*( )([/]*(whatever|any|tank[s]*|heal[s]*|healer[s]*|dps|pvp|lf|lfm|lfg|looking|mara|diremaul|zg|zf|rfd|bfd|ubrs|lbrs|uld|ulda|aq|aq20|aq40|st|brd|sfk|sm|dm|deadmine[s]*|stockade[s]*|stock[s]*|gnomer|gnomeregan|strat|scholo|scholomance|dungeon)[/]*\\b).*', re.IGNORECASE)
LFG_PATTERN = re.compile(ANYTHING + WORD +
                         group(
                             group(LOOKING_REGEX + ANYTHING + ROLE_CLASS_REGEX) + EXIST + OR +
                             group(ROLE_CLASS_REGEX + ANYTHING + LOOKING_REGEX) + EXIST + OR +
                             group(LOOKING_REGEX) + EXIST
                         ) + ANYTHING + SPACE +
                         group(SLASH + ANY +
                               group(ANYTHING_REGEX + OR + PVP_REGEX + OR + DUNGEON_REGEX)
                               + SLASH + ANY) +
                         WORD + ANYTHING, re.IGNORECASE)
BOOST_PATTERN = re.compile(ANYTHING + WORD + BOOST_REGEX + WORD + ANYTHING, re.IGNORECASE)
GUILD_PATTERN = re.compile(ANYTHING +
                           group(
                               group(LB + EMOJI_REGEX + ANY + LETTERS + EMOJI_REGEX + ANY + RB) + OR +
                               group(LC + EMOJI_REGEX + ANY + LETTERS + EMOJI_REGEX + ANY + RC)
                           ) + ANYTHING, re.IGNORECASE)

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
GUILDCHATLOGGER_ADDON = BACK_SLASH + 'GuildChatLogger'
OFFICERCHATLOGGER_ADDON = BACK_SLASH + 'OfficerChatLogger'
SYSTEMCHATLOGGER_ADDON = BACK_SLASH + 'SystemChatLogger'
LFGCHATLOGGER_ADDON = BACK_SLASH + 'LFGChatLogger'




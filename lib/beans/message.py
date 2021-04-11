import logging
import re
import time
import pytz
from datetime import datetime

import settings
from lib.utils import constants

LOG = logging.getLogger(__name__)


class Message:
    """Message class to hold properties parsed from World of Warcraft logging addons"""
    def __init__(self, timestamp, player, line):
        self.timestamp = timestamp
        self.player = player
        self.line = replace_enchant_patterns(replace_item_patterns(replace_raidmarks(replace_mentions(replace_escape_sequences(line)))))

    def __lt__(self, other) -> bool:
        if type(other) is Message:
            return float(self.timestamp) < float(other.timestamp)
        else:
            return float(self.timestamp) < float(other)

    def __gt__(self, other) -> bool:
        if type(other) is Message:
            return float(self.timestamp) > float(other.timestamp)
        else:
            return float(self.timestamp) > float(other)

    def __eq__(self, other) -> bool:
        return type(other) is Message and self.timestamp == other.timestamp and self.player == other.player and self.line == other.line

    def __hash__(self):
        return hash(('timestamp', self.timestamp, 'player', self.player, 'line', self.line))

    def __str__(self) -> str:
        if is_dst():
            readable_timestamp = time.strftime('%I:%M:%S %p', time.gmtime(float(self.timestamp) - 14400))
        else:
            readable_timestamp = time.strftime('%I:%M:%S %p', time.gmtime(float(self.timestamp) - 18000))
        return ("`[" + readable_timestamp + "]` [" + self.player + "]: " + self.line).encode("LATIN-1", "ignore").decode("UTF-8", "ignore")


def is_dst() -> bool:
    """Checks whether or not Daylight Saving Time is active or not in the Eastern Timezone"""
    return not (pytz.timezone('US/Eastern').localize(datetime(year=datetime.now().year, month=1, day=1)).utcoffset() == datetime.now().utcoffset())


def replace_escape_sequences(line: str) -> str:
    """Replaces any escape sequences found in the string that will interfere with Discord"""
    if '*' in line:
        LOG.debug("Mutating(escape_sequences): " + line)
        line = line.replace('*', '\*')
    return line


def replace_mentions(line: str) -> str:
    """Replaces any mentions found in the string that will interfere with Discord"""
    debug = 'Mutating(mentions): '
    if '@everyone' in line:
        LOG.debug(debug + line)
        line = line.replace('@everyone', 'everyone')
    if '@here' in line:
        LOG.debug(debug + line)
        line = line.replace('@here', 'here')
    return line


def replace_raidmarks(line: str) -> str:
    """Replaces World of Warcraft raid markers found in the string with corresponding Discord emojis"""
    debug = 'Mutating(raidmarks): '
    if constants.SKULL in line:
        LOG.debug(debug + line)
        line = line.replace(constants.SKULL, settings.load()['discord']['skull_emoji'])
    if constants.CROSS in line:
        LOG.debug(debug + line)
        line = line.replace(constants.CROSS, settings.load()['discord']['cross_emoji'])
    if constants.SQUARE in line:
        LOG.debug(debug + line)
        line = line.replace(constants.SQUARE, settings.load()['discord']['square_emoji'])
    if constants.MOON in line:
        LOG.debug(debug + line)
        line = line.replace(constants.MOON, settings.load()['discord']['moon_emoji'])
    if constants.TRIANGLE in line:
        LOG.debug(debug + line)
        line = line.replace(constants.TRIANGLE, settings.load()['discord']['triangle_emoji'])
    if constants.DIAMOND in line:
        LOG.debug(debug + line)
        line = line.replace(constants.DIAMOND, settings.load()['discord']['diamond_emoji'])
    if constants.CIRCLE in line:
        LOG.debug(debug + line)
        line = line.replace(constants.CIRCLE, settings.load()['discord']['circle_emoji'])
    if constants.STAR in line:
        LOG.debug(debug + line)
        line = line.replace(constants.STAR, settings.load()['discord']['star_emoji'])
    return line


def replace_item_patterns(line):
    return replace_pattern('Mutating(item_patterns): ', constants.ITEM_PATTERN, line, constants.ITEM_REPLACE_REGEX, constants.WOWHEAD_ITEM_URL)


def replace_enchant_patterns(line):
    return replace_pattern('Mutating(enchant_patterns): ', constants.ENCHANT_PATTERN, line, constants.ENCHANT_REPLACE_REGEX, constants.WOWHEAD_SPELL_URL)


def replace_pattern(debug, pattern, line, regex, url):
    if pattern.match(line):
        LOG.debug(debug + line)
        split_message = line.split('|r')
        line = ''
        for split in split_message:
            split_match = pattern.match(split + '|r')
            if split_match:
                split = re.sub(regex, url + split_match.group(2), split + '|r')
                line = line + split + ' '
            else:
                line = line + split
    return line

import logging
import re
import time
import pytz
from datetime import datetime

from lib.utils import constants

LOG = logging.getLogger(__name__)

class Message:
    def __init__(self, timestamp, player, line):
        self.timestamp = timestamp
        self.player = player
        self.line = replace_enchant_patterns(replace_item_patterns(replace_raidmarks(replace_mentions(replace_escape_sequences(line)))))

    def __lt__(self, other):
        if type(other) is Message:
            return float(self.timestamp) < float(other.timestamp)
        else:
            return float(self.timestamp) < float(other)

    def __gt__(self, other):
        if type(other) is Message:
            return float(self.timestamp) > float(other.timestamp)
        else:
            return float(self.timestamp) > float(other)

    def __str__(self):
        if is_dst():
            readable_timestamp = time.strftime('%I:%M:%S %p', time.gmtime(float(self.timestamp) - 14400))
        else:
            readable_timestamp = time.strftime('%I:%M:%S %p', time.gmtime(float(self.timestamp) - 18000))
        return ("`[" + readable_timestamp + "]` [" + self.player + "]: " + self.line).encode("LATIN-1", "ignore").decode("UTF-8", "ignore")


def is_dst():
    return not (pytz.timezone('US/Eastern').localize(datetime(year=datetime.now().year, month=1, day=1)).utcoffset() == datetime.now().utcoffset())


def replace_escape_sequences(line):
    if '*' in line:
        LOG.debug("Mutating(escape_sequences): " + line)
        line = line.replace('*', '\*')
    return line


def replace_mentions(line):
    if '@everyone' in line:
        LOG.debug("Mutating(mentions): " + line)
        line = line.replace('@everyone', 'everyone')
    if '@here' in line:
        LOG.debug("Mutating(mentions): " + line)
        line = line.replace('@here', 'here')
    return line


def replace_raidmarks(line):
    if '{skull}' in line:
        LOG.debug("Mutating(raidmarks): " + line)
        line = line.replace('{skull}', '<:m1:653845160668430338>')
    if '{cross}' in line:
        LOG.debug("Mutating(raidmarks): " + line)
        line = line.replace('{cross}', '<:m2:653845153991360512>')
    if '{square}' in line:
        LOG.debug("Mutating(raidmarks): " + line)
        line = line.replace('{square}', '<:m3:653845142809346097>')
    if '{moon}' in line:
        LOG.debug("Mutating(raidmarks): " + line)
        line = line.replace('{moon}', '<:m4:653845133883736075>')
    if '{triangle}' in line:
        LOG.debug("Mutating(raidmarks): " + line)
        line = line.replace('{triangle}', '<:m5:653845123830120502>')
    if '{diamond}' in line:
        LOG.debug("Mutating(raidmarks): " + line)
        line = line.replace('{diamond}', '<:m6:653845114694664205>')
    if '{circle}' in line:
        LOG.debug("Mutating(raidmarks): " + line)
        line = line.replace('{circle}', '<:m7:653845107346374666>')
    if '{star}' in line:
        LOG.debug("Mutating(raidmarks): " + line)
        line = line.replace('{star}', '<:m8:653845093027151872>')
    return line


def replace_item_patterns(line):
    if constants.ITEM_PATTERN.match(line):
        LOG.debug("Mutating(item_patterns): " + line)
        split_message = line.split('|r')
        line = ''
        for split in split_message:
            split_match = constants.ITEM_PATTERN.match(split + '|r')
            if split_match:
                item_id = split_match.group(2)
                split = re.sub(constants.ITEM_REPLACE_REGEX, constants.WOWHEAD_ITEM_URL + item_id, split + '|r')
                line = line + split + ' '
            else:
                line = line + split
    return line


def replace_enchant_patterns(line):
    if constants.ENCHANT_PATTERN.match(line):
        LOG.debug("Mutating(enchant_patterns): " + line)
        split_message = line.split('|r')
        line = ''
        for split in split_message:
            split_match = constants.ENCHANT_PATTERN.match(split + '|r')
            if split_match:
                spell_id = split_match.group(2)
                split = re.sub(constants.ENCHANT_REPLACE_REGEX, constants.WOWHEAD_SPELL_URL + spell_id, split + '|r')
                line = line + split + ' '
            else:
                line = line + split
    return line

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
        self.line = replace_item_patterns(replace_mentions(replace_escape_sequences(line)))

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

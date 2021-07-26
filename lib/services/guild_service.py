"""Handles loading and parsing World of Warcraft Guild Info"""
import logging
import re
import time

import settings
from lib.beans.member import Member

LOG = logging.getLogger(__name__)


def get_guild_members(is_online: bool = True):
    """Returns the Members found from the Guild Info file"""
    return parse_guild_members(load_guild_info(), is_online)


def load_guild_info():
    """Loads the World of Warcraft Guild Info file"""
    data = None
    while data is None:
        try:
            with open(settings.load()['wow']['guild_info_file'], mode='r', encoding='UTF-8') as data_file:
                data = data_file.readlines()
        except OSError:
            LOG.warning('Loading guild info file failed, retrying...', exc_info=True)
            time.sleep(1)
    return data


def parse_guild_members(data, is_online: bool = True):
    """Parses the Guild Info file into Members"""
    data_start = None
    members = []
    for index, line in enumerate(data):
        if index < len(data) - 2:
            if re.match('GUILDINFO = {', data[index]):
                data_start = index
            if data_start is not None and ((index - data_start) % 12) == 0:
                member = parse_guild_member(index, data)
                if is_online and is_online != member.online:
                    continue
                members.append(member)
    members.sort()
    return members


def parse_guild_member(index, data):
    """Parses a section of the Guild Info file into a Member"""
    name = data[index + 1].split('"')[1].split('-')[0]
    guild_index = int(data[index + 2].split(',')[0].strip())
    timestamp = float(data[index + 3].split(',')[0].strip())
    rank = data[index + 4].split('"')[1]
    level = int(data[index + 5].split(',')[0].strip())
    zone = data[index + 6].split(', --')[0]
    if zone == "nil":
        zone = "Unknown"
    else:
        zone = zone.strip()[1:][:-1]
    note = data[index + 7].split(', --')[0].strip()[1:][:-1]
    officernote = data[index + 8].split(', --')[0].strip()[1:][:-1]
    online = data[index + 9].split(',')[0].strip()
    if online == "true":
        online = True
    else:
        online = False
    status = int(data[index + 10].split(',')[0].strip())
    if status == 1:
        status = "Away"
    elif status == 2:
        status = "Busy"
    else:
        status = "Available"
    clazz = data[index + 11].split('"')[1].title()
    return Member(guild_index, timestamp, name, rank, level, zone, note, officernote, online, status, clazz)

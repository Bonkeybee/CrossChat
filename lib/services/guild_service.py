import logging
import re
import time

import settings
from lib.beans.member import Member

LOG = logging.getLogger(__name__)


def load_members(is_online: bool):
    data = None
    while data is None:
        try:
            with open(settings.load()['wow']['guild_info_file'], mode='r', encoding='UTF-8') as data_file:
                data = data_file.readlines()
        except OSError:
            LOG.warning('Loading guild info file failed, retrying...', exc_info=True)
            time.sleep(1)

    data_start = None
    members = []
    for i, line in enumerate(data):
        if i < len(data) - 2:
            if re.match('GUILDINFO = {', data[i]):
                data_start = i
            if data_start is not None and ((i - data_start) % 12) == 0:
                name = data[i + 1].split('"')[1].split('-')[0]
                index = data[i + 2].split(',')[0].strip()
                timestamp = data[i + 3].split(',')[0].strip()
                rank = data[i + 4].split('"')[1]
                level = data[i + 5].split(',')[0].strip()
                zone = data[i + 6].split('"')[1]
                note = data[i + 7].split(', --')[0].strip()[1:][:-1]
                officernote = data[i + 8].split(', --')[0].strip()[1:][:-1]
                online = data[i + 9].split(',')[0].strip()
                status = data[i + 10].split(',')[0].strip()
                clazz = data[i + 11].split('"')[1]
                member = Member(index, timestamp, name, rank, level, zone, note, officernote, online, status, clazz)

                if is_online is not None and is_online != member.online:
                    continue

                members.append(member)
    members.sort()
    return members

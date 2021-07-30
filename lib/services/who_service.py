"""Handles pulling guild info for a who report"""
from lib.services.guild_service import get_guild_members
from lib.utils import constants


def detailed_who(level, name):
    """Generates a detailed who report"""
    members = filter_members_by_name(name, filter_members_by_level(level, get_guild_members(False)))
    message = '**Found ' + str(members.__len__()) + ' matches:**\n'
    for member in members:
        message += member.__str__() + '\n'
    return message


def simple_who():
    """Generates a simple who report with just name, class, and level"""
    members = get_guild_members()
    message = '**' + str(members.__len__()) + ' members online:**\n'
    for member in members:
        message += member.__simple__() + '\n'
    message = message[:constants.DISCORD_MESSAGE_LIMIT-3] + (message[constants.DISCORD_MESSAGE_LIMIT-3:] and '...')
    return message


def filter_members_by_level(level, members):
    """Handles the level filtering"""
    if level:
        if '+' in level:
            level = int(''.join(filter(str.isdigit, level)))
            members = list(filter(lambda m: m.level >= level, members))
        elif '-' in level:
            level = int(''.join(filter(str.isdigit, level)))
            members = list(filter(lambda m: m.level <= level, members))
        else:
            level = int(''.join(filter(str.isdigit, level)))
            members = list(filter(lambda m: m.level == level, members))
    return members

def filter_members_by_name(name, members):
    """Handles the name filtering"""
    if name:
        members = list(filter(lambda m: str.lower(name) in str.lower(m.name), members))
    return members

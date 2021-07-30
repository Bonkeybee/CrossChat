"""Handles performing the Discord/Member role auditing"""
import settings
from lib.services.guild_service import get_guild_members


def check_discord_members_for_name_in_note(discord_members) -> str:
    """Checks each discord member if they are actually a member"""
    message = ''
    game_members = get_guild_members(False)
    for discord_member in discord_members:
        if has_member_role(discord_member) and not is_discord_member_actual_member(discord_member, game_members):
            message = message + '(<@' + str(discord_member.id) + '>) is not a guild member (set note or kick)\n'
    return message


def has_member_role(discord_member):
    """Checks if the discord member has the member role"""
    for role in discord_member.roles:
        if role.id == int(settings.load()['discord']['member_role']):
            return True
    return False

def is_discord_member_actual_member(discord_member, game_members):
    """Checks if the discord member username is part of the member"""
    for game_member in game_members:
        if game_member.officernote == discord_member.__str__():
            return True
    return False


def check_members_for_name_match_and_permissions(discord_members) -> str:
    """Checks if the discord member nickname matches the member or if they don't have the member role"""
    message = ''
    game_members = get_guild_members(False)
    for game_member in game_members:
        discord_member = find_member_with_matching_note(game_member, discord_members)
        if discord_member:
            if has_member_role(discord_member):
                if str.lower(game_member.name) not in str.lower(discord_member.display_name):
                    message = message + game_member.name + '(<@' + str(discord_member.id) + '>) character and discord name (' + discord_member.display_name + ') does not match (change nickname or move note)\n'
            else:
                message = message + game_member.name + '(<@' + str(discord_member.id) + '>) does not have member permissions (grant or remove note)\n'
    return message


def find_member_with_matching_note(game_member, guild_members):
    """Finds the matching discord member from the member"""
    for discord_member in guild_members:
        if game_member.officernote == discord_member.__str__():
            return discord_member
    return None

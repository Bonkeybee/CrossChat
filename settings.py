"""Loads the project config file"""
import os
import configparser
from lib.utils import constants


config = None


def load():
    """Load the config file or return the cache"""
    global config
    if config is None:
        config = configparser.ConfigParser()
        config.read(os.getcwd()+'\\'+constants.CONFIG_FILE)
    return config


USER_CHANNEL_IDS = {int(load()['discord']['guild_crosschat_channel_id']): 'guild', int(load()['discord']['officer_crosschat_channel_id']): 'officer'}

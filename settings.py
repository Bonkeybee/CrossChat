import os
import configparser
from lib.utils import constants


config = None


def load():
    global config
    if config is None:
        config = configparser.ConfigParser()
        config.read(os.getcwd()+'\\'+constants.CONFIG_FILE)
    return config

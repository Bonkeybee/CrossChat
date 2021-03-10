import configparser

from lib.utils import constants

config = configparser.ConfigParser()


def load_config(base_dir):
    config.read(base_dir+'\\'+constants.CONFIG_FILE)
    debug = False
    if not config.has_section('discord'):
        debug = True
        config.read(base_dir+'\\'+constants.SAMPLE_CONFIG_FILE)
    return config, debug

import logging

from lib.utils import constants

LOG = logging.getLogger(__name__)
last_timestamp: float = 0


def save_state(timestamp, config):
    global last_timestamp
    last_timestamp = timestamp
    if last_timestamp != 0:
        LOG.info("Saving timestamp " + str(last_timestamp))
        config['state'] = {}
        config['state']['guild_timestamp'] = str(last_timestamp)
        with open(constants.CONFIG_FILE, 'w') as configfile:
            config.write(configfile)


def load_state(config):
    global last_timestamp
    if last_timestamp == 0 and config.has_section('state') and config.has_option('state', 'guild_timestamp'):
        last_timestamp = float(config['state']['guild_timestamp'])
        LOG.info("Loaded timestamp " + str(last_timestamp))
    return last_timestamp or 0

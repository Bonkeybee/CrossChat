import logging

from lib.utils import constants

LOG = logging.getLogger(__name__)

timestamps = {}


def save_state(timestamp, channel, config):
    global timestamps
    if timestamp != 0:
        LOG.info("Saving timestamp " + str(timestamp))
        timestamps[channel] = timestamp
        config['state'] = {}
        config['state'][channel+'_timestamp'] = str(timestamp)
        with open(constants.CONFIG_FILE, 'w') as configfile:
            config.write(configfile)


def load_state(channel, config):
    global timestamps
    if timestamps.get(channel) is None and config.has_section('state') and config.has_option('state', channel+'_timestamp'):
        timestamps[channel] = float(config['state'][channel+'_timestamp'])
        LOG.info("Loaded timestamp " + str(timestamps.get(channel)))
    return timestamps.get(channel) or 0

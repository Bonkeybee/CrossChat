import logging

import settings
from lib.utils import constants

LOG = logging.getLogger(__name__)

timestamps = {}


def save_state(timestamp, channel):
    global timestamps
    if timestamp != 0:
        LOG.info("Saving timestamp " + str(timestamp))
        timestamps[channel] = timestamp
        if not settings.load().has_section('state'):
            settings.load()['state'] = {}
        settings.load()['state'][channel+'_timestamp'] = str(timestamp)
        with open(constants.CONFIG_FILE, 'w') as configfile:
            settings.load().write(configfile)


def load_state(channel):
    global timestamps
    if timestamps.get(channel) is None and settings.load().has_section('state') and settings.load().has_option('state', channel+'_timestamp'):
        timestamps[channel] = float(settings.load()['state'][channel+'_timestamp'])
        LOG.info("Loaded timestamp " + str(timestamps.get(channel)))
    return timestamps.get(channel) or 0

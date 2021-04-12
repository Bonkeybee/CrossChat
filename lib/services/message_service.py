import logging
import time

import requests

from lib.beans.message import Message
from lib.services.state_service import load_state, save_state

LOG = logging.getLogger(__name__)


def is_new_message(message, channel):
    if load_state(channel) < message:
        return True
    return False


def add_message(messages, timestamp, player, line, channel):
    message = Message(timestamp, player, line)
    if is_new_message(message, channel):
        messages.append(message)


def combine_messages(i, j, messages):
    bulk_message = ''
    for index in range(i, j):
        bulk_message = bulk_message + str(messages[index]) + '\n'
    return bulk_message


def push(url, timestamp, content, channel):
    status = 0
    while status == 0 or status == 429:
        response = requests.post(url=url, data={'content': content})
        status = response.status_code
        if status == 429:
            LOG.info('waiting for request limit...')
            time.sleep(1)
    save_state(timestamp, channel)
    LOG.info(content)


def push_all(url, messages, channel):
    messages_length = len(messages)
    bulk_index = 0
    while messages_length > 0 and bulk_index < messages_length:
        max_index = min(bulk_index + 6, messages_length)
        bulk_message = combine_messages(bulk_index, max_index, messages)
        bulk_index = max_index
        push(url, float(messages[bulk_index - 1].timestamp), bulk_message, channel)

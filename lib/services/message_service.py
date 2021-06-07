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


def push_with_retries(url, timestamp, content, channel, attempts):
    response = requests.post(url=url, data={'content': content})
    if response.status_code == 429:
        LOG.info('waiting for request limit...')
        time.sleep(pow(attempts + 1, 2))
        return push_with_retries(url, timestamp, content, channel, attempts + 1)
    else:
        save_state(timestamp, channel)
        LOG.info(content.encode("UTF-8", "ignore").decode("UTF-8", "ignore"))


def push_all(url, messages, channel):
    messages_length = len(messages)
    bulk_index = 0
    while messages_length > 0 and bulk_index < messages_length:
        max_index = min(bulk_index + 6, messages_length)
        bulk_message = combine_messages(bulk_index, max_index, messages)
        bulk_index = max_index
        push_with_retries(url, float(messages[bulk_index - 1].timestamp), bulk_message, channel, 0)

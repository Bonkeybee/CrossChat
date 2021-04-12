import logging
import time

LOG = logging.getLogger(__name__)


def parse_chat_log(index, chat_log):
    timestamp = chat_log[index].split('[')[1].split(']')[0]
    player = chat_log[index + 1].split('"')[1]
    line = chat_log[index + 2].replace('\\"', '\'').split('"')[1]
    return timestamp, player, line


def load_chat_log(path):
    chat_log = None
    while chat_log is None:
        try:
            with open(path, mode='r', encoding='UTF-8') as chat_log_file:
                chat_log = chat_log_file.readlines()
        except Exception as exception:
            LOG.error(exception)
            time.sleep(1)
    return chat_log

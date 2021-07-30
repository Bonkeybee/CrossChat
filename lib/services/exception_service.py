"""Handles sending exceptions"""
import logging

from settings import USER_CHANNEL_IDS

LOG = logging.getLogger(__name__)


async def send_exception(exception, bot):
    """Send encountered exceptions to discord"""
    LOG.exception('Unexpected exception: ' + repr(exception), exception)
    for key in USER_CHANNEL_IDS:
        await bot.get_channel(key).send('Unexpected exception: ' + repr(exception))


async def send_user_exception(channel, error_type, user, message):
    """Send user exception back to the user"""
    await channel.send(error_type + ": " + user + " - " + message)

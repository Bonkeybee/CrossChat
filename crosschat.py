"""Handles the discord<->game portion of crosschat"""
import asyncio
import logging
import os
import re
import time
from collections import OrderedDict
from contextlib import closing
from http import HTTPStatus
from os import system

import discord
from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
from discord import ClientException, HTTPException, app_commands
from tendo import singleton

import settings
from lib.beans.message import Message
from lib.services.audit_service import check_discord_members_for_name_in_note, check_members_for_name_match_and_permissions
from lib.services.chat_log_service import load_chat_log, parse_chat_log
from lib.services.exception_service import send_exception
from lib.services.message_service import add_message, handle_user_message, push_all
from lib.services.restart_service import handle_restart
from lib.services.who_service import detailed_who, simple_who
from lib.utils import constants

system('title ' + 'crosschat')
singleton.SingleInstance()

# noinspection PyArgumentList
logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.INFO,
    handlers=[
        logging.FileHandler(filename="log.log", mode='w'),
        logging.StreamHandler()
    ])
LOG = logging.getLogger(__name__)
LOG.info("Starting CROSSCHAT...")

intents = discord.Intents.all()
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)
voice_client = None
session = Session(profile_name="CrosschatPolly")
polly = session.client("polly")
speech_lock = asyncio.Lock()


# noinspection PyBroadException
async def chat_log_to_discord_webhook(chat_log_file_option, starting_key, channel, webhook_url_option, embed_name, embed_channel_id_option, embed_message_id_option, bad_patterns, good_patterns):
    """Reads the World of Warcraft addon chat logs and pushes new messages to the Discord webhook and/or embed"""
    await wait_until_ready()
    try:
        while True:
            messages = get_chat_log_messages(chat_log_file_option, starting_key, channel)
            if embed_name and embed_channel_id_option and embed_message_id_option:
                messages = await handle_embed(messages, embed_name, embed_channel_id_option, embed_message_id_option, bad_patterns, good_patterns)
            if messages:
                push_all(settings.load()['discord'][webhook_url_option], messages, channel)
            if channel == "guild" and (await get_voice_client()).is_connected():
                for message in messages:
                    await play_with_retry(message.player + " says: " + message.raw, "sounds/text.mp3", "Joanna")
            await asyncio.sleep(constants.CHAT_LOG_CYCLE_TIME)
    except Exception as e:
        await send_exception(e, bot)


async def play_with_retry(text, path, voice):
    """Synthesizes text into speech as an audio file and queues it to the audio client stream"""
    await speech_lock.acquire()
    try:
        speech = None
        try:
            speech = polly.synthesize_speech(Text=text, OutputFormat="mp3", VoiceId=voice, Engine="neural")
        except (BotoCoreError, ClientError) as error:
            LOG.error(error)
        if speech is not None:
            while (await get_voice_client()).is_playing():
                await asyncio.sleep(0.1)
            with closing(speech["AudioStream"]) as stream:
                with open(path, "wb") as file:
                    file.write(stream.read())
            await asyncio.sleep(0.1)
            try:
                (await get_voice_client()).play(discord.FFmpegPCMAudio(executable="ffmpeg.exe", source=path))
            except ClientException:
                await asyncio.sleep(1)
                await play_with_retry((await get_voice_client()), path, voice)
    finally:
        speech_lock.release()


def get_chat_log_messages(chat_log_file_option, starting_key, channel):
    """Loads and parses the World of Warcraft chat log and returns a sorted list of message objects"""
    chat_log = load_chat_log(settings.load()['wow'][chat_log_file_option])
    data_start = None
    messages = []
    for index, line in enumerate(chat_log):
        if index < len(chat_log) - 1:
            if re.match(starting_key, chat_log[index]):
                data_start = index + 1
            if data_start is not None and ((index + data_start) % 4) == 0:
                timestamp, player, message = parse_chat_log(index, chat_log)
                add_message(messages, timestamp, player, message, channel)
    messages.sort()
    return messages


async def handle_embed(messages: list[Message], embed_name, embed_channel_id_option, embed_message_id_option, bad_patterns, good_patterns) -> list[Message]:
    """Process messages """
    if messages:
        if settings.load().has_section('state') and settings.load().has_option('state', embed_message_id_option):
            discord_message: discord.Message = await bot.get_channel(int(settings.load()['discord'][embed_channel_id_option])).fetch_message(int(settings.load()['state'][embed_message_id_option]))
            if not discord_message.embeds:
                return await create_or_update_embed(discord_message, [], messages, embed_name, embed_channel_id_option, embed_message_id_option, bad_patterns, good_patterns)
            old_messages = get_old_messages_from_embed(discord_message.embeds[0])
            old_messages.sort()
            return await create_or_update_embed(discord_message, old_messages, messages, embed_name, embed_channel_id_option, embed_message_id_option, bad_patterns, good_patterns)
        else:
            return await create_or_update_embed(None, [], messages, embed_name, embed_channel_id_option, embed_message_id_option, bad_patterns, good_patterns)
    else:
        await refresh_embed(embed_channel_id_option, embed_message_id_option)


async def create_or_update_embed(discord_message, old_messages, new_messages, embed_name, embed_channel_id_option, embed_message_id_option, bad_patterns, good_patterns):
    """Create or update a discord embed"""
    embedded_messages, non_embedded_messages = filter_new_messages(new_messages, bad_patterns, good_patterns)
    embed = discord.Embed(title=embed_name, description=new_messages[-1].timestamp)
    messages_to_embed = old_messages + embedded_messages
    messages_to_embed = list(OrderedDict.fromkeys(messages_to_embed))
    messages_to_embed.sort()
    message_map = {}
    for message in messages_to_embed:
        message_map[message.player] = message
    messages_to_embed = list(message_map.values())
    messages_to_embed.sort(reverse=True)
    add_embed_fields(messages_to_embed, embed)
    if discord_message:
        await discord_message.edit(embed=embed)
    else:
        discord_message = await bot.get_channel(int(settings.load()['discord'][embed_channel_id_option])).send(embed=embed)
        settings.load()['state'][embed_message_id_option] = str(discord_message.id)
        with open(constants.CONFIG_FILE, 'w') as configfile:
            settings.load().write(configfile)
    return non_embedded_messages


def filter_new_messages(new_messages, bad_patterns, good_patterns):
    """Filter the messages and return the messages that will and will not be embedded"""
    embedded_messages = []
    non_embedded_messages = []
    for message in new_messages:
        if has_bad_pattern(message, bad_patterns):
            continue
        if has_good_pattern(message, good_patterns):
            embedded_messages.append(message)
        else:
            non_embedded_messages.append(message)
    return embedded_messages, non_embedded_messages


def has_bad_pattern(message, bad_patterns):
    """Check if the message has any bad patterns"""
    for pattern in bad_patterns:
        if pattern.match(message.line):
            return True
    return False


def has_good_pattern(message, good_patterns):
    """Check if the message has any good patterns"""
    for pattern in good_patterns:
        if pattern.match(message.line):
            return True
    return False


async def refresh_embed(embed_channel_id_option, embed_message_id_option):
    """Refresh the messages in the embed with new timestamps"""
    if settings.load().has_section('state') and settings.load().has_option('state', embed_message_id_option):
        discord_message: discord.Message = await get_message_with_retry(int(settings.load()['discord'][embed_channel_id_option]), int(settings.load()['state'][embed_message_id_option]), 0)
        if not discord_message or not discord_message.embeds:
            return
        old_messages = get_old_messages_from_embed(discord_message.embeds[0])
        old_messages.sort(reverse=True)
        embed = discord.Embed(title=discord_message.embeds[0].title, description=discord_message.embeds[0].description)
        add_embed_fields(old_messages, embed)
        await discord_message.edit(embed=embed)


async def get_message_with_retry(channel_id, message_id, attempts):
    """Gets a discord message with 5 retries"""
    try:
        return await bot.get_channel(channel_id).fetch_message(message_id)
    except HTTPException as exception:
        if exception.code == HTTPStatus.GATEWAY_TIMEOUT and attempts <= constants.DISCORD_RETRY_LIMIT:
            await asyncio.sleep(pow(attempts + 1, 2))
            return await get_message_with_retry(channel_id, message_id, attempts + 1)


def get_old_messages_from_embed(discord_embed):
    """Parse the previously sent messages from the embed"""
    old_messages = []
    for field in discord_embed.fields:
        if field.name and field.value:
            timestamp = field.value.split('|')[-1]
            if any(c in 'abcdefABCDEF' for c in timestamp):
                timestamp_major = int(timestamp.split('.')[0], 16)
                timestamp_minor = int(timestamp.split('.')[1], 16)
                timestamp = str(timestamp_major) + '.' + str(timestamp_minor)
            player = field.name.strip()
            line = ':'.join(field.value.split(':')[1:]).strip()
            if line:
                message = Message(timestamp, player, line)
                old_messages.append(message)
    return old_messages


def add_embed_fields(old_messages, embed):
    """Add messages to the embed fields"""
    for message in old_messages:
        message.line = re.compile('\\b(tank|tanks)\\b', re.IGNORECASE).sub('<@&' + settings.load()['discord']['tank_role'] + '>', message.line)
        message.line = re.compile('\\b(heal|heals|healer)\\b', re.IGNORECASE).sub('<@&' + settings.load()['discord']['heal_role'] + '>', message.line)
        message.line = re.compile('\\b(dps)\\b', re.IGNORECASE).sub('<@&' + settings.load()['discord']['dps_role'] + '>', message.line)
        message.line = re.compile('\\b(all)\\b', re.IGNORECASE).sub('<@&' + settings.load()['discord']['tank_role'] + '><@&' + settings.load()['discord']['heal_role'] + '><@&' + settings.load()['discord']['dps_role'] + '>', message.line)
        duration = int((float(time.time()) - float(message.timestamp)) / 60)
        if duration <= 60:
            readable_duration = str(duration) + 'm: '
            if duration == 0:
                readable_duration = 'now: '
            timestamp_major = hex(int(message.timestamp.split('.')[0]))[2:]
            timestamp_minor = hex(int(message.timestamp.split('.')[1]))[2:]
            message.line = message.line.rsplit('|', 1)[0]

            count = 0
            for field in embed.fields:
                count += len(field.name) + len(field.value)
            if count < constants.DISCORD_EMBED_LIMIT:
                embed.add_field(name=message.player.strip(), value=((readable_duration + message.line).strip() + ' | ' + (timestamp_major + '.' + timestamp_minor).strip()), inline=True)
            else:
                return


async def get_voice_client():
    """Initializes the discord voice client"""
    global voice_client
    if voice_client is None:
        voice_client = await bot.get_channel(int(settings.load()['discord']['guild_general_voice_channel_id'])).connect()
    return voice_client


# DISCORD STUFF
async def wait_until_ready():
    """Waits until all aspects of the discord bot is ready"""
    while voice_client is None:
        await asyncio.sleep(1)
    assert(voice_client is not None)
    while bot is None:
        await asyncio.sleep(1)
    assert(bot is not None)
    await bot.wait_until_ready()


@bot.event
async def on_ready():
    """Indicator for when the bot connects to discord"""
    await get_voice_client()
    await tree.sync(guild=discord.Object(id=int(settings.load()['discord']['guild_id'])))
    LOG.info(bot.user.name + ' has connected to Discord!')
    if not os.path.exists("sounds"):
        os.makedirs("sounds")
    asyncio.get_running_loop().create_task(chat_log_to_discord_webhook('guild_chat_log_file', 'GUILDCHATLOG = {', 'guild', 'guild_chat_webhook_url', None, None, None, None, None))
    asyncio.get_running_loop().create_task(chat_log_to_discord_webhook('officer_chat_log_file', 'OFFICERCHATLOG = {', 'officer', 'officer_chat_webhook_url', None, None, None, None, None))
    asyncio.get_running_loop().create_task(chat_log_to_discord_webhook('system_chat_log_file', 'SYSTEMCHATLOG = {', 'system', 'system_chat_webhook_url', None, None, None, None, None))
    asyncio.get_running_loop().create_task(chat_log_to_discord_webhook('lfg_chat_log_file', 'LFGCHATLOG = {', 'lfg', 'lfg_chat_webhook_url', 'LookingForGroup', 'lfg_crosschat_channel_id', 'lfg_embed_message_id', [constants.LAZY_LFG_PATTERN, constants.BOOST_PATTERN, constants.GUILD_PATTERN, constants.RECRUITING_PATTERN], [constants.LFG_PATTERN]))
    LOG.info('Tasks initialized!')


@bot.event
async def on_message(message):
    """Discord message handling"""
    if not message.author.bot:
        await handle_user_message(message)


@tree.command(name="restart", description="Restarts the CROSSCHAT service", guild=discord.Object(id=int(settings.load()['discord']['guild_id'])))
@app_commands.checks.has_role(int(settings.load()['discord']['admin_role']))
async def restart(context: discord.Interaction):
    """Restarts the CROSSCHAT service"""
    await context.response.send_message("Restarting CROSSCHAT, standby...")
    await handle_restart()


@tree.command(name="audit", description="Generates an audit report which contains members with mismatched permissions or names", guild=discord.Object(id=int(settings.load()['discord']['guild_id'])))
@app_commands.checks.has_role(int(settings.load()['discord']['admin_role']))
async def audit(context: discord.Interaction):
    """Generates an audit report which contains members with mismatched permissions or names"""
    await safe_send_message(context, '**Generating Audit Report:** \n')
    await safe_send_message(context, check_discord_members_for_name_in_note(context.guild.members))
    await safe_send_message(context, check_members_for_name_match_and_permissions(context.guild.members))
    await safe_send_message(context, '**Audit Report Complete**')


# @tree.command(name="who", description="Generates a who report which contains character data from the game", guild=discord.Object(id=int(settings.load()['discord']['guild_id'])))
# @app_commands.checks.has_role(int(settings.load()['discord']['member_role']))
# @ibot.command(name="who", description="shows who is online in the guild", scope=int(settings.load()['discord']['guild_id']), default_member_permissions=interactions.Permissions.ADMINISTRATOR,
#               options=[
#                   interactions.Option(name="level", description="example: 60", type=interactions.OptionType.STRING, required=False),
#                   interactions.Option(name="name", description="example: Bonkeybee", type=interactions.OptionType.STRING, required=False)
#               ])
# async def who(context: discord.Interaction, level: str = None, name: str = None):
#     """Generates a who report which contains character data from the game"""
#     if level or name:
#         await safe_send_message(context, detailed_who(level, name))
#     else:
#         await safe_send_message(context, simple_who())


async def self_delete(message, duration):
    """Waits the specified duration and then deletes the discord message"""
    await asyncio.sleep(duration)
    await message.delete()


async def safe_send_message(context: discord.Interaction, message):
    """Sends a message to discord that auto-deletes after a minute"""
    if len(message) > 0:
        message = message[:constants.DISCORD_MESSAGE_LIMIT - 3] + (message[constants.DISCORD_MESSAGE_LIMIT - 3:] and '...')
        if context.response.is_done():
            await context.followup.send(message)
        else:
            await context.response.send_message(message)
        return True
    return False


sanity = Message(0, "Player", "LFM N Shattered Halls. Need @Heals. Summons Rdy.PST {Moon}")
if has_good_pattern(sanity, [constants.LFG_PATTERN]):
    bot.run(settings.load()['discord']['token'])
else:
    LOG.error('Failed sanity check!')

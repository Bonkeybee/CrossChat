import subprocess
print(subprocess.check_output(["git", "pull"]))

import configparser
config = configparser.ConfigParser()
config.read('config.ini')
ADDON_PATH = config['wow']['ADDON_PATH']

import shutil


BACK_SLASH = '\\'
GUILDCHATLOGGER_ADDON = 'GuildChatLogger'

shutil.rmtree(ADDON_PATH + BACK_SLASH + GUILDCHATLOGGER_ADDON, True)
shutil.copytree(GUILDCHATLOGGER_ADDON, ADDON_PATH + BACK_SLASH + GUILDCHATLOGGER_ADDON)

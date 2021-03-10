import configparser
import shutil
import subprocess

from lib.utils import constants

print(subprocess.check_output(["git", "pull"]))


config = configparser.ConfigParser()
config.read(constants.CONFIG_FILE)
ADDON_PATH = config['wow']['addon_path']


shutil.rmtree(ADDON_PATH + constants.BACK_SLASH + constants.GUILDCHATLOGGER_ADDON, True)
shutil.copytree(constants.GUILDCHATLOGGER_ADDON, ADDON_PATH + constants.BACK_SLASH + constants.GUILDCHATLOGGER_ADDON)

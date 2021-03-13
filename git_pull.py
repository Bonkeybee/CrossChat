import configparser
import shutil
import subprocess

from lib.utils import constants

print(subprocess.check_output(["git", "pull"]))


config = configparser.ConfigParser()
config.read(constants.CONFIG_FILE)
ADDON_PATH = config['wow']['addon_path']


print('removing ' + ADDON_PATH + constants.BACK_SLASH + constants.GUILDCHATLOGGER_ADDON)
shutil.rmtree(ADDON_PATH + constants.BACK_SLASH + constants.GUILDCHATLOGGER_ADDON, True)
print('copying ' + constants.ADDONS + constants.BACK_SLASH + constants.GUILDCHATLOGGER_ADDON + ' to ' + ADDON_PATH + constants.BACK_SLASH + constants.GUILDCHATLOGGER_ADDON)
shutil.copytree(constants.ADDONS + constants.BACK_SLASH + constants.GUILDCHATLOGGER_ADDON, ADDON_PATH + constants.BACK_SLASH + constants.GUILDCHATLOGGER_ADDON)

print('removing ' + ADDON_PATH + constants.BACK_SLASH + constants.OFFICERCHATLOGGER_ADDON)
shutil.rmtree(ADDON_PATH + constants.BACK_SLASH + constants.OFFICERCHATLOGGER_ADDON, True)
print('copying ' + constants.ADDONS + constants.BACK_SLASH + constants.OFFICERCHATLOGGER_ADDON + ' to ' + ADDON_PATH + constants.BACK_SLASH + constants.OFFICERCHATLOGGER_ADDON)
shutil.copytree(constants.ADDONS + constants.BACK_SLASH + constants.OFFICERCHATLOGGER_ADDON, ADDON_PATH + constants.BACK_SLASH + constants.OFFICERCHATLOGGER_ADDON)

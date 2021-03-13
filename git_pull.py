import configparser
import shutil
import subprocess

from lib.utils import constants

print(subprocess.check_output(["git", "pull"]))


config = configparser.ConfigParser()
config.read(constants.CONFIG_FILE)
ADDON_PATH = config['wow']['addon_path']


def update_addon(src_path, wow_path):
    print('removing ' + wow_path)
    shutil.rmtree(wow_path, True)
    print('copying ' + src_path + ' to ' + wow_path)
    shutil.copytree(src_path, wow_path)


WOW_GUILDCHATLOGGER_PATH = ADDON_PATH + constants.BACK_SLASH + constants.GUILDCHATLOGGER_ADDON
SRC_GUILDCHATLOGGER_PATH = constants.ADDONS + constants.BACK_SLASH + constants.GUILDCHATLOGGER_ADDON
update_addon(SRC_GUILDCHATLOGGER_PATH, WOW_GUILDCHATLOGGER_PATH)

WOW_OFFICERCHATLOGGER_PATH = ADDON_PATH + constants.BACK_SLASH + constants.OFFICERCHATLOGGER_ADDON
SRC_OFFICERCHATLOGGER_PATH = constants.ADDONS + constants.BACK_SLASH + constants.OFFICERCHATLOGGER_ADDON
update_addon(SRC_OFFICERCHATLOGGER_PATH, WOW_OFFICERCHATLOGGER_PATH)

WOW_SYSTEMCHATLOGGER_PATH = ADDON_PATH + constants.BACK_SLASH + constants.SYSTEMCHATLOGGER_ADDON
SRC_SYSTEMCHATLOGGER_PATH = constants.ADDONS + constants.BACK_SLASH + constants.SYSTEMCHATLOGGER_ADDON
update_addon(SRC_SYSTEMCHATLOGGER_PATH, WOW_SYSTEMCHATLOGGER_PATH)

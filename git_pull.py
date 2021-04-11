import shutil
import subprocess

from lib.utils import constants
import settings


print(subprocess.check_output(["git", "pull"]))


def update_addon(src_path, wow_path):
    print('removing ' + wow_path)
    shutil.rmtree(wow_path, True)
    print('copying ' + src_path + ' to ' + wow_path)
    shutil.copytree(src_path, wow_path)


update_addon(constants.ADDONS + constants.BACK_SLASH + constants.GUILDCHATLOGGER_ADDON, settings.load()['wow']['addon_path'] + constants.BACK_SLASH + constants.GUILDCHATLOGGER_ADDON)
update_addon(constants.ADDONS + constants.BACK_SLASH + constants.OFFICERCHATLOGGER_ADDON, settings.load()['wow']['addon_path'] + constants.BACK_SLASH + constants.OFFICERCHATLOGGER_ADDON)
update_addon(constants.ADDONS + constants.BACK_SLASH + constants.SYSTEMCHATLOGGER_ADDON, settings.load()['wow']['addon_path'] + constants.BACK_SLASH + constants.SYSTEMCHATLOGGER_ADDON)
update_addon(constants.ADDONS + constants.BACK_SLASH + constants.LFGCHATLOGGER_ADDON, settings.load()['wow']['addon_path'] + constants.BACK_SLASH + constants.LFGCHATLOGGER_ADDON)

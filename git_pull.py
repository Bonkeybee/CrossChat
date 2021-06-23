"""Updates the source code of the repo and its dependencies"""
import shutil
import subprocess

import settings
from lib.utils import constants

print(subprocess.check_output(["git", "pull"]))


def update_addon(addon):
    """Removes and then copies the specified World of Warcraft addon to addons directory"""
    print('removing ' + settings.load()['wow']['addon_path'] + addon)
    shutil.rmtree(settings.load()['wow']['addon_path'] + addon, True)
    print('copying ' + constants.ADDONS + addon + ' to ' + settings.load()['wow']['addon_path'] + addon)
    shutil.copytree(constants.ADDONS + addon, settings.load()['wow']['addon_path'] + addon)


update_addon(constants.GUILDCHATLOGGER_ADDON)
update_addon(constants.OFFICERCHATLOGGER_ADDON)
update_addon(constants.SYSTEMCHATLOGGER_ADDON)
update_addon(constants.LFGCHATLOGGER_ADDON)
update_addon(constants.GUILDINFO_ADDON)

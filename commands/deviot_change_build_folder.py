from sublime_plugin import WindowCommand
from ..api import deviot
from ..libraries.tools import save_setting


class DeviotChangeBuildFolderCommand(WindowCommand):
    """
    Adds extra libraries folder path from the settings
    """

    def run(self):
        deviot.folder_explorer(key='build_folder', callback=save_setting)

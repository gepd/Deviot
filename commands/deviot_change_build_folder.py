from sublime_plugin import WindowCommand
from ..libraries.tools import save_setting
from ..libraries.paths import folder_explorer

class DeviotChangeBuildFolderCommand(WindowCommand):
    """
    Adds extra libraries folder path from the settings
    """

    def run(self):
        folder_explorer(key='build_folder', callback=save_setting)
from sublime_plugin import WindowCommand
from ..libraries.tools import save_setting
from ..libraries.paths import folder_explorer

class DeviotExtraLibraryFolderCommand(WindowCommand):
    """
    Adds extra libraries folder path from the settings
    """

    def run(self):
        folder_explorer(key='extra_library', callback=save_setting)
from sublime_plugin import WindowCommand
from ..api import deviot
from ..libraries.tools import save_setting


class DeviotExtraLibraryFolderCommand(WindowCommand):
    """
    Adds extra libraries folder path from the settings
    """

    def run(self):
        deviot.folder_explorer(key='lib_extra_dirs', callback=self.done)

    def done(self, key, value):
        save_setting(key, value)
        self.window.run_command('deviot_rebuild_syntax')

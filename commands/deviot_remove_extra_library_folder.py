from sublime_plugin import WindowCommand
from ..libraries.tools import get_setting, save_setting


class DeviotRemoveExtraLibraryFolderCommand(WindowCommand):
    """
    Removes extra libraries folder path from the settings
    """

    def run(self):
        save_setting('lib_extra_dirs', None)
        self.window.run_command('deviot_rebuild_syntax')

    def is_enabled(self):
        extra = get_setting('lib_extra_dirs', None)
        return bool(extra)

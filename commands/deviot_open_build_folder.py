from sublime_plugin import WindowCommand
from sublime import run_command
from ..libraries.paths import getTempPath

class DeviotOpenBuildFolderCommand(WindowCommand):
    """
    Show the PlatformIO web site.

    Extends: sublime_plugin.WindowCommand
    """

    def run(self):
        temp_path = getTempPath()
        self.window.run_command('open_dir', {'dir': temp_path})
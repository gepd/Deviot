from sublime_plugin import WindowCommand
from sublime import run_command

from ..api import deviot
from ..libraries.tools import get_setting

class DeviotOpenBuildFolderCommand(WindowCommand):
    """
    Show the PlatformIO web site.

    Extends: sublime_plugin.WindowCommand
    """

    def run(self):
        build_folder = get_setting('build_folder', None)
        if(not build_folder):
            build_folder = deviot.temp_path()
        
        self.window.run_command('open_dir', {'dir': build_folder})
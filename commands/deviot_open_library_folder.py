from sublime_plugin import WindowCommand
from sublime import run_command, active_window

from os import path
from ..api import deviot
from ..libraries.tools import make_folder


class DeviotOpenLibraryFolderCommand(WindowCommand):
    """
    Open a new window where the user libreries must be installed

    Extends: sublime_plugin.TextCommand
    """

    def run(self):
        pio_library = deviot.pio_library()
        self.window.run_command('open_dir', {'dir': pio_library})

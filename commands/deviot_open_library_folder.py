from sublime_plugin import WindowCommand
from sublime import run_command, active_window

from os import path
from ..libraries.tools import make_folder
from ..libraries.paths import getPioLibrary

class DeviotOpenLibraryFolderCommand(WindowCommand):
    """
    Open a new window where the user libreries must be installed

    Extends: sublime_plugin.TextCommand
    """

    def run(self):
        pio_library = getPioLibrary()
        self.window.run_command('open_dir', {'dir': pio_library})
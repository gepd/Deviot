from sublime_plugin import TextCommand
from sublime import run_command

from ..libraries.paths import getPioLibrary

class DeviotOpenLibraryFolderCommand(TextCommand):
    """
    Open a new window where the user libreries must be installed

    Extends: sublime_plugin.TextCommand
    """

    def run(self, edit):
        pio_library = getPioLibrary()
        run_command('open_url', {'url': pio_library})
from sublime_plugin import TextCommand
from sublime import run_command

from os import path
from ..libraries.tools import make_folder
from ..libraries.paths import getPioLibrary

class DeviotOpenLibraryFolderCommand(TextCommand):
    """
    Open a new window where the user libreries must be installed

    Extends: sublime_plugin.TextCommand
    """

    def run(self, edit):
        pio_library = getPioLibrary()
        
        if(not path.exists(pio_library)):
            make_folder(pio_library)

        run_command('open_url', {'url': pio_library})
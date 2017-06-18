from sublime_plugin import WindowCommand
from ..libraries.libraries import Libraries

class DeviotRemoveLibraryCommand(WindowCommand):
    def run(self):
        Libraries().get_installed_list()
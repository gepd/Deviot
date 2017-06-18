from sublime_plugin import WindowCommand
from ..libraries.libraries import Libraries

class DeviotSearchLibraryCommand(WindowCommand):
    def run(self):
        Libraries().search_library()
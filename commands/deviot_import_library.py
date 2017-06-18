from sublime_plugin import WindowCommand
from ..libraries.quick_menu import QuickMenu

class DeviotImportLibraryCommand(WindowCommand):
    def run(self):
        QuickMenu().quick_import()
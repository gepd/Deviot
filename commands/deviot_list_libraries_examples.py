from sublime_plugin import WindowCommand
from ..libraries.quick_menu import QuickMenu

class DeviotListLibraryExamplesCommand(WindowCommand):
    def run(self):
        QuickMenu().quick_libraries()
from sublime_plugin import WindowCommand
from ..libraries.quick_menu import QuickMenu

class DeviotLanguagesCommand(WindowCommand):
    def run(self):
        QuickMenu().quick_language()
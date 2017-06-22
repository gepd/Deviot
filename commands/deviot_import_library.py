from sublime_plugin import WindowCommand
from ..libraries.quick_menu import QuickMenu
from ..libraries.project_check import ProjectCheck

class DeviotImportLibraryCommand(WindowCommand):
    def run(self):
        QuickMenu().quick_import()

    def is_enabled(self):
        is_iot = ProjectCheck().is_iot()
        return bool(is_iot)
from sublime_plugin import WindowCommand
from ..libraries.quick_menu import QuickMenu
from ..libraries.project_check import ProjectCheck

class DeviotImportLibraryCommand(WindowCommand):
    def run(self):
        Quick = QuickMenu()
        items = Quick.import_list()
        callback = Quick.callback_import
        Quick.set_list(items)

        Quick.show_quick_panel(callback)

    def is_enabled(self):
        is_iot = ProjectCheck().is_iot()
        return bool(is_iot)
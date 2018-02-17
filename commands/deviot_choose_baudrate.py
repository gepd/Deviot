from sublime_plugin import WindowCommand
from ..libraries.quick_menu import QuickMenu

class DeviotChooseBaudrateCommand(WindowCommand):
    """
    Stores the baudrate selected for the user and save it in
    the preferences file.

    Extends: sublime_plugin.WindowCommand
    """

    def run(self):
        Quick = QuickMenu()
        items = Quick.serial_baudrate_list()
        callback = Quick.callback_serial_baudrate
        Quick.set_list(items)

        Quick.show_quick_panel(callback)
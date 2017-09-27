from sublime_plugin import WindowCommand
from ..libraries.quick_menu import QuickMenu

class DeviotSelectPortCommand(WindowCommand):
    def run(self):
        Quick = QuickMenu()
        items = Quick.serial_list()
        callback = Quick.callback_serial_ports
        Quick.set_list(items)

        Quick.show_quick_panel(callback)
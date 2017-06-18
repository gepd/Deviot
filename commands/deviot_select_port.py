from sublime_plugin import WindowCommand
from ..libraries.quick_menu import QuickMenu

class DeviotSelectPortCommand(WindowCommand):
    def run(self):
        QuickMenu().quick_serial_ports()
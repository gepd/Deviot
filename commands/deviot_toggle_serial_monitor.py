from sublime_plugin import WindowCommand
from ..libraries import serial
from ..libraries.quick_menu import QuickMenu


class DeviotToggleSerialMonitorCommand(WindowCommand):
    def run(self):
        Quick = QuickMenu()
        self.items = Quick.serial_list()
        Quick.set_list(self.items)
        Quick.show_quick_panel(self.callback)

    def callback(self, selected):
        port_id = self.items[selected][2]
        serial.toggle_serial_monitor(port_id)

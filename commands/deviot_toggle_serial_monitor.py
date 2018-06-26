from sublime_plugin import WindowCommand
from ..libraries import serial
from ..libraries.quick_menu import QuickMenu


class DeviotToggleSerialMonitorCommand(WindowCommand):
    def run(self):
        serial.toggle_serial_monitor()
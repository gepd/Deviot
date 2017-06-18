from sublime_plugin import WindowCommand
from ..libraries import serial

class DeviotToggleSerialMonitorCommand(WindowCommand):
    def run(self):
        serial.toggle_serial_monitor()
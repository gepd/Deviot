from sublime_plugin import WindowCommand
from ..libraries import serial
from ..libraries.tools import get_setting

class DeviotCleanConsoleCommand(WindowCommand):
    monitor = None

    def run(self):
        self.monitor.clean_console()

    def is_enabled(self):
        port_id = get_setting('port_id', None)

        if(port_id and port_id in serial.serials_in_use):
            self.monitor = serial.serial_monitor_dict[port_id]
            
            if(self.monitor.is_running):
                return True
        return False
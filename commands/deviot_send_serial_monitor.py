from sublime_plugin import WindowCommand
from ..libraries import serial
from ..libraries.tools import get_setting

class DeviotSendSerialMonitorCommand(WindowCommand):
    text_send = None

    def run(self):
        caption = 'send'
        self.window.show_input_panel(caption, '', self.on_done, None, self.on)

    def on_done(self, text):
        self.text_send(text)

    def is_enabled(self):
        port_id = get_setting('port_id', None)

        if(port_id and port_id in serial.serials_in_use):
            monitor = serial.serial_monitor_dict[port_id]
            
            if(monitor.is_running):
                self.text_send = monitor.send
                return True
        return False
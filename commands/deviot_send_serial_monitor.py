from sublime_plugin import WindowCommand
from ..libraries import serial
from ..libraries.tools import get_setting

class DeviotSendSerialMonitorCommand(WindowCommand):
    text_send = None
    output_console = None

    def run(self):
        caption = 'send'
        self.window.show_input_panel(caption, '', self.on_done, None, self.on_cancel)

    def on_done(self, text):
        self.text_send(text)
        
        if(self.output_console):
            self.window.run_command('deviot_show_console')

    def on_cancel(self):
        if(self.output_console):
            self.window.run_command('deviot_show_console')

    def is_enabled(self):
        port_id = get_setting('port_id', None)
        self.output_console = get_setting('output_console', False)

        if(port_id and port_id in serial.serials_in_use):
            monitor = serial.serial_monitor_dict[port_id]
            
            if(monitor.is_running):
                self.text_send = monitor.send
                return True
        return False
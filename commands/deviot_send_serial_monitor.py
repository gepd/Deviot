from sublime_plugin import TextCommand
from ..libraries import serial
from ..libraries.tools import get_setting
from .deviot_history import history

class DeviotSendSerialMonitorCommand(TextCommand):
    text_send = None
    output_console = None
    window = None

    def run(self, edit):
        self.window = self.view.window()
        caption = 'send'
        v = self.window.show_input_panel(caption, '', self.on_done, None, self.on_cancel)
        v.settings().set('deviotInputText', True)

    def on_done(self, text):
        history.insert(text)
        self.text_send(text)
        self.window.run_command('deviot_send_serial_monitor')
        
        if(self.output_console):
            self.window.run_command('deviot_show_console')

    def on_cancel(self):
        history.reset_index()
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
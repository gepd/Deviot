from sublime_plugin import WindowCommand
from ..libraries.tools import get_sysetting, save_setting

class DeviotSetIpCommand(WindowCommand):
    """
    Stores the ip to use in OTA Upload

    """

    def run(self):
        from ..libraries.I18n import I18n

        _ = I18n().translate

        caption = _("add_ip_caption")
        self.window.show_input_panel(caption, '', self.on_done, None, None)

    def on_done(self, ip):
        save_setting('port_id', ip)
        if(get_sysetting('last_action', None)):
            self.window.run_command("deviot_upload_sketch")
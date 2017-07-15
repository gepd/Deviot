from sublime_plugin import WindowCommand
from ..libraries.tools import get_sysetting, save_setting

class DeviotSetPasswordCommand(WindowCommand):
    """
    Stores the password to use in OTA Upload

    """

    def run(self):
        from ..libraries.I18n import I18n

        _ = I18n().translate

        caption = _("pass_caption")
        self.window.show_input_panel(caption, '', self.on_done, None, None)

    def on_done(self, password):
        save_setting('auth_pass', password)
        if(get_sysetting('last_action', None)):
            self.window.run_command("deviot_upload_sketch")
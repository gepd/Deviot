from sublime_plugin import WindowCommand
from ..libraries.tools import get_sysetting


class DeviotDeveloperPio(WindowCommand):
    """
    Stores the autmatic scroll selected for the user and save it in
    the preferences file.

    Extends: sublime_plugin.WindowCommand
    """

    def run(self):
        self.window.run_command("deviot_dev_pio")

    def is_checked(self):
        return get_sysetting('pio_developer', False)

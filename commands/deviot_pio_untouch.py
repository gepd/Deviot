from sublime_plugin import WindowCommand
from ..libraries.tools import get_setting, save_setting

class DeviotPioUntouchCommand(WindowCommand):
    """
    Stores the pio untouch option selected for the user and save
    it in the preferences file.

    Extends: sublime_plugin.WindowCommand
    """

    def run(self):
        pio_untouch = get_setting('pio_untouch', False)
        save_setting('pio_untouch',not pio_untouch)

    def is_checked(self):
        return get_setting('pio_untouch', False)
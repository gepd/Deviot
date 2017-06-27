from sublime_plugin import WindowCommand
from ..libraries.tools import get_setting, save_setting
from ..platformio.update import Update

class DeviotDeveloperPio(WindowCommand):
    """
    Stores the autmatic scroll selected for the user and save it in
    the preferences file.

    Extends: sublime_plugin.WindowCommand
    """

    def run(self):
        pio_developer = get_setting('pio_developer', False)
        save_setting('pio_developer', not pio_developer)
        Update().developer_async()


    def is_checked(self):
        return get_setting('pio_developer', False)
from sublime_plugin import WindowCommand
from ..libraries.tools import get_setting, save_setting

class DeviotChooseBaudrateCommand(WindowCommand):
    """
    Stores the baudrate selected for the user and save it in
    the preferences file.

    Extends: sublime_plugin.WindowCommand
    """

    def run(self, baudrate_item):
        save_setting('baudrate', baudrate_item)

    def is_checked(self, baudrate_item):
        target_baudrate = get_setting('baudrate', 9600)
        return baudrate_item == target_baudrate
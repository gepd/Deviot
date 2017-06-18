from sublime_plugin import WindowCommand
from ..libraries.tools import get_setting, save_setting

class DeviotChooseDisplayModeCommand(WindowCommand):
    """
    Stores the display mode option selected for the user and save it in
    the preferences file.

    Extends: sublime_plugin.WindowCommand
    """

    def run(self, display_mode_item):
        save_setting('display_mode', display_mode_item)

    def is_checked(self, display_mode_item):
        display_target = get_setting('display_mode', 'Text')
        return display_mode_item == display_target
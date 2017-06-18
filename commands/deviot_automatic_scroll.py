from sublime_plugin import WindowCommand
from ..libraries.tools import get_setting, save_setting

class DeviotAutomaticScrollCommand(WindowCommand):
    """
    Stores the autmatic scroll selected for the user and save it in
    the preferences file.

    Extends: sublime_plugin.WindowCommand
    """

    def run(self):
        automatic_scroll = get_setting('automatic_scroll', True)
        save_setting('automatic_scroll',not automatic_scroll)

    def is_checked(self):
        return get_setting('automatic_scroll', True)
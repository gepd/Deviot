from sublime_plugin import WindowCommand
from ..libraries.tools import get_setting, save_setting

class DeviotAutoCleanCommand(WindowCommand):
    """
    Stores the automatic monitor cleaning user selection
    and save it in the preferences file.

    Extends: sublime_plugin.WindowCommand
    """

    def run(self):
        auto_clean = get_setting('auto_clean', True)
        save_setting('auto_clean',not auto_clean)

    def is_checked(self):
        return get_setting('auto_clean', True)
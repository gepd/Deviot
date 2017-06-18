from sublime_plugin import WindowCommand
from ..libraries.tools import get_setting, save_setting

class DeviotChooseLineEndingCommand(WindowCommand):
    """
    Stores the line ending selected for the user and save it in
    the preferences file.

    Extends: sublime_plugin.WindowCommand
    """

    def run(self, line_ending_item):
        save_setting('line_ending', line_ending_item)

    def is_checked(self, line_ending_item):
        target_line_ending = get_setting('line_ending', None)
        return line_ending_item == target_line_ending
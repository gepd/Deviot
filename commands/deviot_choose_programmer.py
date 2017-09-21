from sublime_plugin import WindowCommand
from ..libraries.tools import get_setting, save_setting

class DeviotChooseProgrammerCommand(WindowCommand):
    """
    Stores the programmer selected for the user and save it in
    the preferences file.

    Extends: sublime_plugin.WindowCommand
    """

    def run(self, programmer_item):
        save_setting('programmer_id', programmer_item)

    def is_checked(self, programmer_item):
        target_programmer = get_setting('programmer_id', False)
        return programmer_item == target_programmer
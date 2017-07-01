from sublime_plugin import WindowCommand
from ..libraries.tools import get_setting, save_setting

class DeviotVerboseOutputCommand(WindowCommand):
    """
    Option to select if use always the platformio structure or not

    Extends: sublime_plugin.WindowCommand
    """
    verbose_output = None
    def run(self):
        save_setting('verbose_output', not self.verbose_output)

    def is_checked(self):
        self.verbose_output = get_setting('verbose_output', False)
        return self.verbose_output
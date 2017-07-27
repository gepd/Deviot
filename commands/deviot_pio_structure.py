from sublime_plugin import WindowCommand
from ..libraries.tools import get_setting, save_setting
from ..libraries.project_check import ProjectCheck

class DeviotPioStructureCommand(WindowCommand):
    """
    Option to select if use always the platformio structure or not

    Extends: sublime_plugin.WindowCommand
    """
    pio_structure = None
    def run(self):
        save_setting('pio_structure', not self.pio_structure)

    def is_checked(self):
        self.pio_structure = get_setting('pio_structure', False)
        return self.pio_structure
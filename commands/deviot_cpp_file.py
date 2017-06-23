from sublime_plugin import WindowCommand
from ..libraries.tools import get_setting, save_setting

class DeviotCppFileCommand(WindowCommand):
    """
    Option to select if use always the platformio structure or not

    Extends: sublime_plugin.WindowCommand
    """
    cpp_file = None
    def run(self):
        save_setting('cpp_file', self.cpp_file)

    def is_checked(self):
        self.cpp_file = get_setting('cpp_file', False)
        return self.cpp_file
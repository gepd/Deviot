from sublime_plugin import WindowCommand
from ..libraries.tools import get_setting, save_setting

class DeviotRebuildSyntaxCommand(WindowCommand):
    """
    Rebuilds sublime-syntax and sublime-completions files

    Extends: sublime_plugin.WindowCommand
    """

    def run(self):
        from ..libraries.syntax import Syntax
        Syntax()
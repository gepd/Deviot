from sublime_plugin import WindowCommand
from ..libraries.tools import get_setting, save_setting

class DeviotOutputConsoleCommand(WindowCommand):
    """
    Stores the output console oprion selected for the user and save it in
    the preferences file.

    Extends: sublime_plugin.WindowCommand
    """

    def run(self):
        output_console = get_setting('output_console', False)
        save_setting('output_console',not output_console)

    def is_checked(self):
        return get_setting('output_console', False)
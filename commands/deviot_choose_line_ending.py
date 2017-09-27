from sublime_plugin import WindowCommand
from ..libraries.quick_menu import QuickMenu

class DeviotChooseLineEndingCommand(WindowCommand):
    """
    Stores the line ending selected for the user and save it in
    the preferences file.

    Extends: sublime_plugin.WindowCommand
    """

    def run(self):
        Quick = QuickMenu()
        items = Quick.line_endings_list()
        callback = Quick.callback_line_endings
        Quick.set_list(items)

        Quick.show_quick_panel(callback)
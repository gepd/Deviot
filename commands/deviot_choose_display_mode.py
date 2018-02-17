from sublime_plugin import WindowCommand
from ..libraries.quick_menu import QuickMenu

class DeviotChooseDisplayModeCommand(WindowCommand):
    """
    Stores the display mode option selected for the user and save it in
    the preferences file.

    Extends: sublime_plugin.WindowCommand
    """

    def run(self):
        Quick = QuickMenu()
        items = Quick.display_mode_list()
        callback = Quick.callback_display_mode
        Quick.set_list(items)

        Quick.show_quick_panel(callback)
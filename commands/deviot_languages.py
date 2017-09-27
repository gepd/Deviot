from sublime_plugin import WindowCommand
from ..libraries.quick_menu import QuickMenu

class DeviotLanguagesCommand(WindowCommand):
    def run(self):
        Quick = QuickMenu()
        items = Quick.language_list()
        callback = Quick.callback_language
        Quick.set_list(items)

        Quick.show_quick_panel(callback)


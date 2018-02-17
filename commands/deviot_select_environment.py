from sublime_plugin import WindowCommand
from ..libraries.quick_menu import QuickMenu
from ..libraries.preferences_bridge import PreferencesBridge

class DeviotSelectEnvironmentCommand(WindowCommand):
    def run(self):
    	Quick = QuickMenu()
    	items = Quick.environment_list()
    	callback = Quick.callback_environment
    	Quick.set_list(items)

    	Quick.show_quick_panel(callback)

    def is_enabled(self):
        selected_boards = PreferencesBridge().get_selected_boards()
        return bool(selected_boards)
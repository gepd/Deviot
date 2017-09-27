from sublime_plugin import WindowCommand
from ..libraries.quick_menu import QuickMenu

class DeviotSelectBoardsCommand(WindowCommand):
    def run(self):
    	Quick = QuickMenu()
    	items = Quick.boards_list()
    	callback = Quick.callback_board
    	Quick.set_list(items)

    	Quick.show_quick_panel(callback)
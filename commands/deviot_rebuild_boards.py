from sublime_plugin import WindowCommand
from ..platformio.pio_bridge import PioBridge

class DeviotRebuildBoardsCommand(WindowCommand):
    """
    Rebuild the boards.json file who is used to list the 
    boards in the quick menu

    Extends: sublime_plugin.WindowCommand
    """

    def run(self):
        PioBridge().save_boards_list_async()
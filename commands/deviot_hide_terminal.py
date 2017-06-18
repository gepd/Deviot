from sublime_plugin import WindowCommand
from ..platformio.pio_terminal import PioTerminal

class DeviotHideTerminalCommand(WindowCommand):

    def run(self):
        PioTerminal().close_terminal()
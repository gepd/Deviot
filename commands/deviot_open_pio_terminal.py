from sublime_plugin import WindowCommand
from ..platformio.pio_terminal import PioTerminal

class DeviotOpenPioTerminalCommand(WindowCommand):

    def run(self):
        PioTerminal().show_input()
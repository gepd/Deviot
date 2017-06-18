from sublime_plugin import WindowCommand
from ..platformio.pio_terminal import PioTerminal

class DeviotShowTerminalCommand(WindowCommand):

    def run(self):
        PioTerminal().show_input()
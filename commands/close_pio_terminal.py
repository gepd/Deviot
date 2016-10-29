
import sublime
import sublime_plugin

from ..platformio.pio_terminal import PioTerminal


class ClosePioTerminalCommand(sublime_plugin.WindowCommand):

    def run(self):
        PioTerminal().close_terminal()

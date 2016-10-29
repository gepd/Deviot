
import sublime
import sublime_plugin

from ..platformio.pio_terminal import PioTerminal


class OpenPioTerminalCommand(sublime_plugin.WindowCommand):

    def run(self):
        PioTerminal().open_terminal()

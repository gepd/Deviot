from sublime_plugin import WindowCommand
from sublime import run_command

class DeviotDonateCommand(WindowCommand):
    """
    Show the Deviot donate website.

    Extends: sublime_plugin.WindowCommand
    """

    def run(self):
        run_command('open_url', {'url': 'https://goo.gl/K0EpFU'})
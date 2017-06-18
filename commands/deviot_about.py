from sublime_plugin import WindowCommand
from sublime import run_command

class DeviotAboutCommand(WindowCommand):
    """
    Show the Deviot github site.

    Extends: sublime_plugin.WindowCommand
    """

    def run(self):
        run_command('open_url', {'url': 'https://goo.gl/c41EXS'})
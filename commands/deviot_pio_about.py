from sublime_plugin import WindowCommand
from sublime import run_command

class DeviotPioAboutCommand(WindowCommand):
    """
    Show the PlatformIO web site.

    Extends: sublime_plugin.WindowCommand
    """

    def run(self):
        run_command('open_url', {'url': 'http://goo.gl/KiXeZL'})
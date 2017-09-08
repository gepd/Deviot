from sublime_plugin import WindowCommand

class DeviotRebuildSyntaxCommand(WindowCommand):
    """
    Rebuilds sublime-syntax and sublime-completions files

    Extends: sublime_plugin.WindowCommand
    """

    def run(self):
        from ..libraries.syntax import Syntax
        Syntax().create_files_async()
from sublime_plugin import WindowCommand


class DeviotRebuildSyntaxCommand(WindowCommand):
    """
    Rebuilds sublime-syntax and sublime-completions files

    Extends: sublime_plugin.WindowCommand
    """

    def run(self):
        self.window.run_command("create_syntax_files")

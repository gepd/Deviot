from sublime_plugin import WindowCommand

class DeviotShowConsoleCommand(WindowCommand):
    """
    Hide the deviot console

    Extends: sublime_plugin.WindowCommand
    """

    def run(self):
        self.window.run_command("show_panel", {"panel": "output.exec"})

from sublime_plugin import WindowCommand

class DeviotHideConsoleCommand(WindowCommand):
    """
    Hide the deviot console

    Extends: sublime_plugin.WindowCommand
    """
    def run(self):
        self.window.run_command("hide_panel", {"panel": "output.exec"})
from sublime_plugin import WindowCommand
from ..libraries.messages import Messages

class DeviotShowConsoleCommand(WindowCommand):
    """
    Hide the deviot console

    Extends: sublime_plugin.WindowCommand
    """

    def run(self):
        output_view = self.window.find_output_panel('deviot')
        if(not output_view):
            messages = Messages()
            messages.create_panel()
            messages.first_message()

        self.window.run_command("show_panel", {"panel": "output.deviot"})

from sublime_plugin import WindowCommand


class DeviotUpgradePioCommand(WindowCommand):
    """
    Search for platformIO updates

    Extends: sublime_plugin.WindowCommand
    """

    def run(self):
        self.window.run_command("deviot_update_pio")

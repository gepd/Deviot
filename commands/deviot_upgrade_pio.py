from sublime_plugin import WindowCommand


class DeviotUpgradePioCommand(WindowCommand):
    """
    Search for platformIO updates

    Extends: sublime_plugin.WindowCommand
    """

    def run(self):
        from ..beginning.update import Update
        Update().update_async()

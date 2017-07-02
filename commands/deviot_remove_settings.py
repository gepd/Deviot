from sublime_plugin import WindowCommand

class DeviotRemoveSettingsCommand(WindowCommand):
    """
    Stores the autmatic scroll selected for the user and save it in
    the preferences file.

    Extends: sublime_plugin.WindowCommand
    """

    def run(self):
        from ..libraries.tools import remove_settings
        remove_settings()
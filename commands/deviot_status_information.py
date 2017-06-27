from sublime_plugin import WindowCommand
from ..libraries.tools import get_setting, save_setting
from ..libraries.preferences_bridge import PreferencesBridge

class DeviotStatusInformationCommand(WindowCommand):
    """
    Activates or deactivates the Deviot information in the status bar
    (board, port)

    Extends: sublime_plugin.WindowCommand
    """

    def run(self):
        status_information = get_setting('status_information', True)
        save_setting('status_information',not status_information)
        PreferencesBridge().set_status_information()

    def is_checked(self):
        return get_setting('status_information', True)
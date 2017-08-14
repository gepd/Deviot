from sublime_plugin import WindowCommand
from ..libraries.tools import get_setting, save_setting

class DeviotSendPersistentCommand(WindowCommand):
    """
    Sets the input text for the serial communication, persistent,
    this means; after send a text, the input text will be displayed
    until press the esc key

    Extends: sublime_plugin.WindowCommand
    """

    def run(self):
        send_persistent = get_setting('send_persistent', True)
        save_setting('send_persistent', not send_persistent)


    def is_checked(self):
        return get_setting('send_persistent', True)
from sublime_plugin import WindowCommand

class DeviotRebuildLibListCommand(WindowCommand):
    """
    Rebuilds the list of libraries file

    Extends: sublime_plugin.WindowCommand
    """

    def run(self):
        from ..libraries.libraries import Libraries
        Libraries().save_installed_list_async()
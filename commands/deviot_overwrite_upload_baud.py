from sublime import Region
from sublime_plugin import WindowCommand
from ..libraries.quick_menu import QuickMenu

class DeviotOverwriteUploadBaudCommand(WindowCommand):

    def run(self):
        QuickMenu().quick_overwrite_baud()
from sublime import Region
from sublime_plugin import WindowCommand
from ..libraries.quick_menu import QuickMenu

class DeviotOverwriteUploadBaudCommand(WindowCommand):

    def run(self):
    	Quick = QuickMenu()
    	items = Quick.overwrite_baud_list()
    	callback = Quick.callback_overwrite_baud
    	Quick.set_list(items)

    	Quick.show_quick_panel(callback)
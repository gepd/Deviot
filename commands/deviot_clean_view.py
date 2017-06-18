from sublime import Region
from sublime_plugin import TextCommand

class DeviotCleanViewCommand(TextCommand):

    def run(self, edit):
        self.view.erase(edit, Region(0, self.view.size()))
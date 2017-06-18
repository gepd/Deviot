from sublime_plugin import TextCommand
from ..libraries.tools import add_library_to_sketch

class DeviotInsertLibraryCommand(TextCommand):
    def run(self, edit, path):
        add_library_to_sketch(self.view, edit, path)
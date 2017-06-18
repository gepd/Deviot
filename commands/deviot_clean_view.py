from sublime_plugin import TextCommand

class DeviotCleanViewCommand(TextCommand):

    def run(self, edit):
        self.view.erase(edit, sublime.Region(0, self.view.size()))
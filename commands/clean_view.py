import sublime
import sublime_plugin


class CleanViewCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        self.view.erase(edit, sublime.Region(0, self.view.size()))

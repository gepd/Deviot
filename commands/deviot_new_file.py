import sublime
import sublime_plugin

from ..libraries.menu import Menu
from ..libraries import paths
from ..libraries. tools import create_sketch, get_config, save_config


class DeviotNewFileCommand(sublime_plugin.WindowCommand):

    def run(self):
        # caption = _('caption_new_sketch')
        self.window.show_input_panel('Name', '', self.location, None, None)

    def location(self, name):
        self.name = name
        last_path = get_config('last_path', None)
        paths.folder_explorer(path=last_path, callback=self.on_done)

    def on_done(self, path):
        create_sketch(path, self.name)
        save_config('last_path', path)

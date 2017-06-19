from sublime_plugin import WindowCommand
from ..libraries.paths import folder_explorer
from ..libraries.tools import create_sketch, get_setting, save_setting


class DeviotNewSketchCommand(WindowCommand):

    def run(self):
        from ..libraries.I18n import I18n

        _ = I18n().translate
        
        caption = _('caption_new_sketch')
        self.window.show_input_panel(caption, '', self.location, None, None)

    def location(self, name):
        self.name = name
        folder_explorer(callback=self.on_done)

    def on_done(self, path):
        create_sketch(self.name, path)
        save_setting('last_path', path)

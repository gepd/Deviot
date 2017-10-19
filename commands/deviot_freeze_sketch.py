from sublime import active_window
from sublime_plugin import WindowCommand
from ..libraries.tools import save_setting, get_setting

class DeviotFreezeSketchCommand(WindowCommand):
    """
    Store the freeze directory
    """
    sketch_path = None
    setting_path = None

    def run(self):
        if(self.setting_path):
            self.sketch_path = None
        save_setting('freeze_sketch', self.sketch_path)

    def is_checked(self):
        return bool(self.setting_path)

    def is_enabled(self):
        enabled = False
        window = active_window()
        view = window.active_view()
        self.sketch_path = view.file_name()

        if(not self.sketch_path):
            return enabled

        self.setting_path = get_setting('freeze_sketch', None)

        if(self.sketch_path.endswith('.ino') or 
            self.sketch_path.endswith('.cpp') or
            self.setting_path):
            enabled = True

        return enabled
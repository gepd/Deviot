from sublime_plugin import WindowCommand
from ..platformio.clean import Clean

class DeviotCleanSketchCommand(WindowCommand):
    def run(self):
        Clean()
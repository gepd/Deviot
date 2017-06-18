from sublime_plugin import WindowCommand
from ..platformio.upload import Upload

class DeviotUploadSketchCommand(WindowCommand):
    def run(self):
        Upload()
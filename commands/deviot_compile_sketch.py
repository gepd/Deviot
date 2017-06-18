from sublime_plugin import WindowCommand
from ..platformio.compile import Compile

class DeviotCompileSketchCommand(WindowCommand):
    def run(self):
        Compile()
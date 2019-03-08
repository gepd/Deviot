from sublime import set_timeout_async
from sublime_plugin import WindowCommand

from ..api import deviot
from ..platformio.pio import Pio
from ..platformio.command import Command

# run commands
command = Command()


class DeviotCompileSketchCommand(WindowCommand):
    def run(self):
        set_timeout_async(Pio(command).compile, 0)


class DeviotUploadSketchCommand(WindowCommand):
    def run(self):
        set_timeout_async(Pio(command).upload, 0)


class DeviotCleanSketchCommand(WindowCommand):
    def run(self):
        set_timeout_async(Pio(command).clean, 0)


class DeviotStopProcessingCommand(WindowCommand):
    def run(self):
        command.run(kill=True)

    def is_enabled(self):
        return command.is_running()

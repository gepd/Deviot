# !/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import sublime
import sublime_plugin
import threading

from .commands import *
from .beginning.pio_install import PioInstall
from .platformio.project_recognition import ProjectRecognition
from .platformio.compile import Compile
from .platformio.upload import Upload
from .platformio.clean import Clean
from .libraries.quick_menu import QuickMenu
from .libraries.top_menu import TopMenu
from .libraries.tools import get_setting, save_setting
from .platformio.initialize import Initialize

from time import sleep

def plugin_loaded():
    compile_lang = get_setting('compile_lang', True)
    if(compile_lang):
        TopMenu().create_main_menu()
        save_setting('compile_lang', False)
    # PioInstall()

class DeviotTestCommand(sublime_plugin.WindowCommand):
    def run(self):
        Initialize()
        # TopMenu()
        pass
class DeviotSelectBoardsCommand(sublime_plugin.WindowCommand):
    def run(self):
        QuickMenu().quick_boards()

class DeviotSelectEnvironmentCommand(sublime_plugin.WindowCommand):
    def run(self):
        QuickMenu().quick_environments()

class DeviotCompileSketchCommand(sublime_plugin.WindowCommand):
    def run(self):
        Compile()

class DeviotUploadSketchCommand(sublime_plugin.WindowCommand):
    def run(self):
        Upload()

class DeviotCleanSketchCommand(sublime_plugin.WindowCommand):
    def run(self):
        Clean()

class DeviotOpenIniFile(sublime_plugin.WindowCommand):

    def run(self):
        views = []

        ini_file = ProjectRecognition().get_ini_path()
        view = self.window.open_file(ini_file)
        views.append(view)

        if views:
            self.window.focus_view(views[0])

    def is_enabled(self):
        from .libraries.project_check import ProjectCheck
        check = ProjectCheck()
        return check.is_iot()


class DeviotSelectPortCommand(sublime_plugin.WindowCommand):
    def run(self):
        QuickMenu().quick_serial_ports()

class DeviotLanguagesCommand(sublime_plugin.WindowCommand):
    def run(self):
        QuickMenu().quick_language()

class HideConsoleCommand(sublime_plugin.WindowCommand):
    """
    Hide the deviot console

    Extends: sublime_plugin.WindowCommand
    """

    def run(self):
        self.window.run_command("hide_panel", {"panel": "output.exec"})


class ShowConsoleCommand(sublime_plugin.WindowCommand):
    """
    Hide the deviot console

    Extends: sublime_plugin.WindowCommand
    """

    def run(self):
        self.window.run_command("show_panel", {"panel": "output.exec"})
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import os
import time
import sublime
import glob
import sublime_plugin
from shutil import rmtree

try:
    from .libs import Paths, Tools
    from .libs.Menu import Menu
    from .libs.Messages import Console
    from .libs.PlatformioCLI import PlatformioCLI
    from .libs.Preferences import Preferences
except:
    from libs import Paths
    from libs import Tools
    from libs.Menu import Menu
    from libs.Messages import Console
    from libs.PlatformioCLI import PlatformioCLI
    from libs.Preferences import Preferences


class DeviotListener(sublime_plugin.EventListener):
    """
    This is the first class to run when the plugin is excecuted
    Extends: sublime_plugin.EventListener
    """

    def __init__(self):
        """
        Checks if platformIO is installed and normally running,
        creates a json file with all boards availables
        """
        if(not PlatformioCLI().platformioCheck()):
            return None

        super(DeviotListener, self).__init__()

        platformio_data = Paths.getTemplateMenuPath(
            'platformio_boards.json', user_path=True)

        if(not os.path.exists(platformio_data)):
            Menu().saveAPIBoards(PlatformioCLI().getAPIBoards)

        Menu().createMainMenu()

    def on_activated(self, view):
        """
        Set the current version of Deviot

        Arguments: view {ST object} -- Sublime Text Object
        """
        Tools.setStatus(view)

    def on_close(self, view):
        """
        When a sketch is closed, temp files are deleted

        Arguments: view {ST object} -- Sublime Text Object
        """
        file_path = Tools.getPathFromView(view)
        if(not file_path):
            return
        file_name = Tools.getFileNameFromPath(file_path, ext=False)
        tmp_path = Paths.getDeviotTmpPath()
        tmp_all = os.path.join(tmp_path, '*')
        tmp_all = glob.glob(tmp_all)

        for content in tmp_all:
            if file_name in content:
                tmp_path = os.path.join(tmp_path, content)
                rmtree(tmp_path, ignore_errors=False)


class PlatformioInstallCommand(sublime_plugin.WindowCommand):
    """
        This command send the user to a website with platformio install
        instructions
    """

    def run(self):
        sublime.run_command('open_url', {'url':
                                         'http://goo.gl/66BHnk'})


class CheckRequirementsCommand(sublime_plugin.WindowCommand):
    """
        Check the if minimum requirements has been established
        detailed information in libs/PlatformioCLI.py
    """

    def run(self):
        PlatformioCLI().platformioCheck()


class SelectBoardCommand(sublime_plugin.WindowCommand):
    """
    This class trigger two methods to know what board(s)
    were chosen and to store it in a preference file.

    Extends: sublime_plugin.WindowCommand
    """

    def run(self, board_id):
        """
        Get the ID of the board selected and store it in a
        preference file.

        Arguments: board_id {string} -- id of the board selected
        """
        Preferences().boardSelected(board_id, Menu().createEnvironmentMenu)

    def is_checked(self, board_id):
        """
        Check if the node in the menu is check or not, this
        function need to return always a bolean

        Arguments: board_id {string} -- id of the board selected
        """
        check = Preferences().checkBoard(board_id)
        return check

    def is_enabled(self):
        return Preferences().get('enable_menu', False)


class MainEnvironmentCommand(sublime_plugin.WindowCommand):
    """
    Enable or disable the "Select environment" menu if none board
    is selected from the list.

    Extends: sublime_plugin.WindowCommand
    """

    def is_enabled(self):
        check = Preferences().get('enable_menu', False)
        if(check):
            check = Preferences().get('env_selected', '')
            if(len(check) == 0):
                check = False
        return check


class SelectEnvCommand(sublime_plugin.WindowCommand):
    """
    Stores the environment option selected by the user in
    the preferences files

    Extends: sublime_plugin.WindowCommand
    """

    def run(self, board_id):
        Preferences().set('env_selected', board_id)

    def is_checked(self, board_id):
        check = Preferences().get('env_selected', False)
        return board_id == check

    def is_enabled(self):
        check = Preferences().get('enable_menu', False)
        return check


class BuildSketchCommand(sublime_plugin.TextCommand):
    """
    Trigger a method to build the files in the current
    view, initializes the console to show the state of
    the process

    Extends: sublime_plugin.TextCommand
    """

    def run(self, edit):
        view = self.view
        console_name = 'Deviot|Build' + str(time.time())
        console = Console(view.window(), name=console_name)
        PlatformioCLI(view, console).openInThread('build')

    def is_enabled(self):
        return Preferences().get('enable_menu', False)


class UploadSketchCommand(sublime_plugin.TextCommand):
    """
    Trigger a method to upload the files in the current
    view, initializes the console to show the state of
    the process

    Extends: sublime_plugin.TextCommand
    """

    def run(self, edit):
        view = self.view
        console_name = 'Deviot|Upload' + str(time.time())
        console = Console(view.window(), name=console_name)
        PlatformioCLI(view, console).openInThread('upload')

    def is_enabled(self):
        is_enabled = Preferences().get('builded_sketch')

        if(not Preferences().get('enable_menu', False)):
            is_enabled = False

        return is_enabled


class CleanSketchCommand(sublime_plugin.TextCommand):
    """
    Trigger a method to delete firmware/program binaries compiled
    if a sketch has been built previously

    Extends: sublime_plugin.TextCommand
    """

    def run(self, edit):
        view = self.view
        console_name = 'Deviot|Clean' + str(time.time())
        console = Console(view.window(), name=console_name)
        PlatformioCLI(view, console).openInThread('clean')

    def is_enabled(self):
        is_enabled = Preferences().get('builded_sketch')

        if(not Preferences().get('enable_menu', False)):
            is_enabled = False

        return is_enabled


class SelectPortCommand(sublime_plugin.WindowCommand):
    """
    Saves the port COM selected by the user in the
    preferences file.

    Extends: sublime_plugin.WindowCommand
    """

    def run(self, id_port):
        Preferences().set('id_port', id_port)

    def is_checked(self, id_port):
        saved_id_port = Preferences().get('id_port')
        return saved_id_port == id_port

    def is_enabled(self):
        return Preferences().get('enable_menu', False)


class ToggleVerboseCommand(sublime_plugin.WindowCommand):
    """
    Saves the verbose output option selected by the user in the
    preferences file.

    Extends: sublime_plugin.WindowCommand
    """

    def run(self):
        verbose = Preferences().get('verbose_output', False)
        Preferences().set('verbose_output', not verbose)

    def is_checked(self):
        return Preferences().get('verbose_output', False)


class AboutDeviotCommand(sublime_plugin.WindowCommand):
    """
    Show the Deviot github site.

    Extends: sublime_plugin.WindowCommand
    """

    def run(self):
        sublime.run_command('open_url', {'url':
                                         'https://goo.gl/c41EXS'})

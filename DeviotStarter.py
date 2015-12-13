#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import os
import sublime
import sublime_plugin

if(int(sublime.version()) < 3000):
    import DeviotFunctions
    import DeviotPaths
else:
    from . import DeviotFunctions
    from . import DeviotPaths


class DeviotListener(sublime_plugin.EventListener):
    """Starter class

    This is the first class to run when the plugin is excecuted

    Extends:
            sublime_plugin.EventListener
    """

    def __init__(self):
        """ Constructor

        In this constructor is setted the version of the
        plugin, and running the creation of the differents
        menus located in the top of sublime text
        """
        self.state_menu = True

        if(not DeviotFunctions.platformioCheck()):
            return None

        super(DeviotListener, self).__init__()

        json_boards_file = DeviotPaths.getDeviotBoardsPath()

        if(not os.path.exists(json_boards_file)):
            DeviotFunctions.Menu().saveAPIBoards()

        DeviotFunctions.Menu().createMainMenu()
        DeviotFunctions.setVersion('0.5')

    def on_activated(self, view):
        """Activated view

        When any tab is activated, this fuction runs.
        From here the plugin detects if the current
        tab is working with any file allowed to working
        with this plugin

        Arguments:
                view {st object} -- stores many info related with ST
        """
        DeviotFunctions.setStatus(view)


class PlatformioInstallCommand(sublime_plugin.WindowCommand):
    """Install
        This command send the user to a website with platformio install
        instructions
    """

    def run(self):
        sublime.run_command('open_url', {'url':
                                         'http://goo.gl/66BHnk'})


class CheckRequirementsCommand(sublime_plugin.WindowCommand):
    """
        Check the if minimum requirements has been established
    """

    def run(self):
        self.state_menu = DeviotFunctions.platformioCheck()


class UpdateMenuCommand(sublime_plugin.WindowCommand):
    """Update/refresh menu

    This command updates the main menu including the list of boards
    vendors/type of board.

    Extends:
            sublime_plugin.WindowCommand
    """

    def run(self):
        DeviotFunctions.Menu().createSerialPortsMenu()

    def is_enabled(self):
        return DeviotFunctions.checkEnvironPath()


class SelectBoardCommand(sublime_plugin.WindowCommand):
    """Select Board Trigger

    This class trigger two methods to know what board(s)
    were chosen and to store it in a preference file.

    Extends:
            sublime_plugin.WindowCommand
    """

    def run(self, board_id):
        """ST method

        Get the ID of the board selected and store it in a
        preference file.

        Arguments:
                board_id {string} -- id of the board selected
        """
        DeviotFunctions.Preferences().boardSelected(board_id)

    def is_checked(self, board_id):
        """ST method

        Check if the node in the menu is check or not, this
        function need to return always a bolean

        Arguments:
                board_id {string} -- id of the board selected
        """
        check = DeviotFunctions.Preferences().checkBoard(board_id)
        return check

    def is_enabled(self):
        return DeviotFunctions.checkEnvironPath()


class BuildSketchCommand(sublime_plugin.TextCommand):
    """Build Sketch Trigger

    This class trigger one method to build the files in the
    current working project

    Extends:
            sublime_plugin.WindowCommand
    """

    def run(self, edit):
        DeviotFunctions.PlatformioCLI(self.view).buildSketchProject()

    def is_enabled(self):
        return DeviotFunctions.checkEnvironPath()


class UploadSketchCommand(sublime_plugin.TextCommand):
    """ST Method

    This class trigger one method to upload the files in the
    current working project

    Extends:
            sublime_plugin.TextCommand
    """

    def run(self, edit):
        DeviotFunctions.PlatformioCLI(self.view).uploadSketchProject()

    def is_enabled(self):
        is_enabled = DeviotFunctions.Preferences().get('builded_sketch')

        if(not DeviotFunctions.checkEnvironPath()):
            is_enabled = False

        return is_enabled


class CleanSketchCommand(sublime_plugin.TextCommand):
    """ST Method

    This class trigger one method to delete compiled object files,
    libraries and firmware/program binaries if a sketch has been
    built previously

    Extends:
            sublime_plugin.TextCommand
    """

    def run(self, edit):
        DeviotFunctions.PlatformioCLI(self.view).cleanSketchProject()

    def is_enabled(self):
        is_enabled = DeviotFunctions.Preferences().get('builded_sketch')

        if(not DeviotFunctions.checkEnvironPath()):
            is_enabled = False

        return is_enabled


class SelectPortCommand(sublime_plugin.WindowCommand):
    """Select port

    Save in the preferences file, the port com to upload the sketch
    when the upload command is use

    Extends:
            sublime_plugin.WindowCommand
    """

    def run(self, id_port):
        DeviotFunctions.Preferences().set('id_port', id_port)

    def is_checked(self, id_port):
        saved_id_port = DeviotFunctions.Preferences().get('id_port')
        return saved_id_port == id_port

    def is_enabled(self):
        return DeviotFunctions.checkEnvironPath()

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
    from .libs.QuickPanel import quickPanel
    from .libs import Libraries
    from .libs.I18n import I18n
except:
    from libs import Paths
    from libs import Tools
    from libs.Menu import Menu
    from libs.Messages import Console
    from libs.PlatformioCLI import PlatformioCLI
    from libs.Preferences import Preferences
    from libs.QuickPanel import quickPanel
    from libs import Libraries
    from libs.I18n import I18n

_ = I18n().translate


class DeviotListener(sublime_plugin.EventListener):
    """
    This is the first class to run when the plugin is excecuted
    Extends: sublime_plugin.EventListener
    """

    def __init__(self):
        """
        Checks if platformIO is installed
        """
        if(not PlatformioCLI().platformioCheck()):
            return None

        super(DeviotListener, self).__init__()

    def on_activated(self, view):
        """
        Set the current version of Deviot

        Arguments: view {ST object} -- Sublime Text Object
        """
        PlatformioCLI(view, command=False).checkInitFile()
        Tools.setStatus(view)

    def on_close(self, view):
        """
        When a sketch is closed, temp files are deleted

        Arguments: view {ST object} -- Sublime Text Object
        """
        keep_cache = Preferences().get('keep_cache', False)
        if(keep_cache):
            return

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
                Preferences().set('builded_sketch', False)

        # Empty enviroment menu
        Menu().createEnvironmentMenu(empty=True)


class PlatformioInstallCommand(sublime_plugin.WindowCommand):
    """
        This command send the user to a website with platformio install
        instructions
    """

    def run(self):
        sublime.run_command('open_url', {'url': 'http://goo.gl/66BHnk'})


class CheckRequirementsCommand(sublime_plugin.TextCommand):
    """
        Check the if minimum requirements has been established
        detailed information in libs/PlatformioCLI.py
    """

    def run(self, edit):
        view = self.view
        console_name = 'Deviot|Check' + str(time.time())
        console = Console(view.window(), name=console_name)
        PlatformioCLI(view, console, True).platformioCheck()


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
        native = Preferences().get('native', False)
        remove = Preferences().boardSelected(board_id)
        if(remove):
            PlatformioCLI().removeEnvFromFile(board_id)
        if(native and not remove):
            Preferences().set('init_queue', board_id)
            PlatformioCLI().openInThread('init')
        Menu().createEnvironmentMenu()

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


class SelectEnvCommand(sublime_plugin.WindowCommand):
    """
    Stores the environment option selected by the user in
    the preferences files

    Extends: sublime_plugin.WindowCommand
    """

    def run(self, board_id):
        native = Preferences().get('native', False)

        key = 'env_selected'
        if(native):
            key = 'native_env_selected'

        Preferences().set(key, board_id)

    def is_checked(self, board_id):
        native = Preferences().get('native', False)

        key = 'env_selected'
        if(native):
            key = 'native_env_selected'

        check = Preferences().get(key, False)
        return board_id == check

    def is_enabled(self):
        return Preferences().get('enable_menu', False)


class SearchLibraryCommand(sublime_plugin.WindowCommand):

    def run(self):
        caption = _('Keyword:')
        self.window.show_input_panel(caption, '', self.on_done, None, None)

    def on_done(self, result):
        Libraries.openInThread('download', self.window, result)


class ShowResultsCommand(sublime_plugin.WindowCommand):

    def run(self):
        choose = Libraries.Libraries().getList()
        quickPanel(self.window, choose, self.on_done)

    def on_done(self, result):
        if(result != -1):
            Libraries.openInThread('install', self.window, result)


class RemoveLibraryCommand(sublime_plugin.WindowCommand):

    def run(self):
        Libraries.openInThread('list', self.window)


class ShowRemoveListCommand(sublime_plugin.WindowCommand):

    def run(self):
        choose = Libraries.Libraries(self.window).installedList()
        quickPanel(self.window, choose, self.on_done)

    def on_done(self, result):
        if(result != -1):
            Libraries.openInThread('remove', self.window, result)


class OpenUserLibraryFolderCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        library = Paths.getUserLibraryPath()
        url = Paths.getOpenFolderPath(library)
        sublime.run_command('open_url', {'url': url})


class ManuallyLibrary(sublime_plugin.WindowCommand):

    def run(self):
        Paths.selectDir(self.window, key='lib_dir', func=Preferences().set)


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
        return Preferences().get('enable_menu')


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


class UpdateBoardListCommand(sublime_plugin.WindowCommand):
    """
    Update the board list, extracting the info from platformIO
    ecosystem

    Extends: sublime_plugin.WindowCommand
    """

    def run(self):
        PlatformioCLI().saveAPIBoards(update_method=Menu().createMainMenu())


class KeepTempFilesCommand(sublime_plugin.WindowCommand):
    """
    When is select avoid to remove the cache from the temporal folder.

    Extends: sublime_plugin.WindowCommand
    """

    def run(self):
        keep = Preferences().get('keep_cache', False)
        Preferences().set('keep_cache', not keep)

    def is_checked(self):
        return Preferences().get('keep_cache', False)


class SelectLanguageCommand(sublime_plugin.WindowCommand):

    def run(self, id_lang):
        Preferences().set('id_lang', id_lang)

    def is_checked(self, id_lang):
        saved_id_lang = Preferences().get('id_lang')
        return saved_id_lang == id_lang


class AboutDeviotCommand(sublime_plugin.WindowCommand):
    """
    Show the Deviot github site.

    Extends: sublime_plugin.WindowCommand
    """

    def run(self):
        sublime.run_command('open_url', {'url': 'https://goo.gl/c41EXS'})

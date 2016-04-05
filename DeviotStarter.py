# !/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import os
import glob
import time
import sublime
import sublime_plugin
import threading
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
    from .libs import Serial
    from .libs import Messages
    from .libs.Progress import ThreadProgress
    from .libs.Install import PioInstall
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
    from libs import Serial
    from libs import Messages
    from libs.Progress import ThreadProgress
    from libs.Install import PioInstall

_ = I18n().translate

package_name = 'Deviot'


def plugin_loaded():
    protected = Preferences().get('protected')
    if(not protected):
        thread = threading.Thread(target=PioInstall().checkPio)
        thread.start()
        ThreadProgress(thread, _('processing'), _('done'))
    else:
        # creating files
        Tools.createCompletions()
        Tools.createSyntaxFile()
        Menu().createMainMenu()
        Menu().createLibraryImportMenu()
        Menu().createLibraryExamplesMenu()

        # Run serial port listener
        Serial_Lib = Serial.SerialListener(func=Menu().createSerialPortsMenu)
        Serial_Lib.start()


def plugin_unloaded():
    try:
        from package_control import events

        if events.remove(package_name):
            Tools.removePreferences()
    except:
        pass

# Compat with ST2
if(int(sublime.version()) < 3000):
    sublime.set_timeout(plugin_loaded, 300)
    unload_handler = plugin_unloaded


class DeviotListener(sublime_plugin.EventListener):
    """
    This is the first class to run when the plugin is excecuted
    Extends: sublime_plugin.EventListener
    """

    def on_activated(self, view):
        """
        Set the current version of Deviot

        Arguments: view {ST object} -- Sublime Text Object
        """
        PlatformioCLI(view, command=False).checkInitFile()
        Tools.setStatus(view)
        Tools.userPreferencesStatus(view)

    def on_close(self, view):
        """
        When a sketch is closed, temp files are deleted

        Arguments: view {ST object} -- Sublime Text Object
        """
        # Serial Monitor
        monitor_module = Serial
        if Messages.isMonitorView(view):
            name = view.name()
            serial_port = name.split('-')[1].strip()
            if serial_port in monitor_module.serials_in_use:
                cur_serial_monitor = monitor_module.serial_monitor_dict.get(
                    serial_port, None)
                if cur_serial_monitor:
                    cur_serial_monitor.stop()
                monitor_module.serials_in_use.remove(serial_port)

        # Remove cache
        keep_cache = Preferences().get('keep_cache', False)
        if(keep_cache):
            return

        file_path = Tools.getPathFromView(view)
        if(not file_path):
            return
        file_name = Tools.getFileNameFromPath(file_path, ext=False)
        tmp_path = Paths.getTempPath()
        tmp_all = os.path.join(tmp_path, '*')
        tmp_all = glob.glob(tmp_all)

        for content in tmp_all:
            if file_name in content:
                tmp_path = os.path.join(tmp_path, content)
                rmtree(tmp_path, ignore_errors=False)
                Preferences().set('builded_sketch', False)

        # Empty enviroment menu
        Menu().createEnvironmentMenu(empty=True)


class DeviotNewSketchCommand(sublime_plugin.WindowCommand):

    def run(self):
        caption = _('caption_new_sketch')
        self.window.show_input_panel(caption, '', self.on_done, None, None)

    def on_done(self, sketch_name):
        Paths.selectDir(self.window, key=sketch_name, func=Tools.createSketch)


class DeviotSelectBoardCommand(sublime_plugin.WindowCommand):
    """
    This class trigger two methods to know what board(s)
    were chosen and to store it in a preference file.

    Extends: sublime_plugin.WindowCommand
    """

    def run(self, board_id):
        native = Preferences().get('native', False)
        remove = Preferences().boardSelected(board_id)
        if(remove):
            PlatformioCLI().removeEnvFromFile(board_id)
        if(native and not remove):
            view = self.window.active_view()
            console_name = 'Deviot|Init' + str(time.time())
            console = Console(view.window(), name=console_name)
            Preferences().set('init_queue', board_id)
            PlatformioCLI(view, console).openInThread('init', chosen=board_id)
        Menu().createEnvironmentMenu()

    def is_checked(self, board_id):
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
        Tools.userPreferencesStatus(self.window.active_view())

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
    """
    Command to search a library in the platformio API

    Extends: sublime_plugin.WindowCommand
    """

    def run(self):
        caption = _('search_query')
        self.window.show_input_panel(caption, '', self.on_done, None, None)

    def on_done(self, result):
        Libraries.openInThread('download', self.window, result)


class ShowResultsCommand(sublime_plugin.WindowCommand):
    """
    The results of the SearchLibraryCommand query in a quick_panel.
    When one of the result is selected, it's installed by CLI

    Extends: sublime_plugin.WindowCommand
    """

    def run(self):
        choose = Libraries.Libraries().getList()
        quickPanel(self.window, choose, self.on_done)

    def on_done(self, result):
        if(result != -1):
            Libraries.openInThread('install', self.window, result)


class RemoveLibraryCommand(sublime_plugin.WindowCommand):
    """
    Remove a library by the CLI

    Extends: sublime_plugin.WindowCommand
    """

    def run(self):
        Libraries.openInThread('list', self.window)


class ShowRemoveListCommand(sublime_plugin.WindowCommand):
    """
    Show the list with all the installed libraries, and what you can remove

    Extends: sublime_plugin.WindowCommand
    """

    def run(self):
        choose = Libraries.Libraries(self.window).installedList()
        quickPanel(self.window, choose, self.on_done)

    def on_done(self, result):
        if(result != -1):
            Libraries.openInThread('remove', self.window, result)


class AddLibraryCommand(sublime_plugin.TextCommand):
    """
    Include the header(s) from the selected library into a sketch

    Extends: sublime_plugin.TextCommand
    """

    def run(self, edit, library_path):
        Tools.addLibraryToSketch(self.view, edit, library_path)


class OpenExampleCommand(sublime_plugin.WindowCommand):
    """
    Open the selected example from the deviot menu

    Extends: sublime_plugin.WindowCommand
    """

    def run(self, example_path):
        Tools.openExample(example_path, self.window)


class OpenLibraryFolderCommand(sublime_plugin.TextCommand):
    """
    Open a new window where the user libreries must be installed

    Extends: sublime_plugin.TextCommand
    """

    def run(self, edit):
        library = Paths.getPioLibrary()
        url = Paths.getOpenFolderPath(library)
        sublime.run_command('open_url', {'url': url})


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


class HideConsoleCommand(sublime_plugin.WindowCommand):
    """
    Hide the deviot console

    Extends: sublime_plugin.WindowCommand
    """

    def run(self):
        self.window.run_command("hide_panel", {"panel": "output.exec"})


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


class AddSerialIpCommand(sublime_plugin.WindowCommand):
    """
    Add a IP to the list of COM ports

    Extends: sublime_plugin.WindowCommand
    """

    def run(self):
        caption = _('add_ip_caption')
        self.window.show_input_panel(caption, '', self.on_done, None, None)

    def on_done(self, result):
        if(result != -1):
            result = (result if result != 0 else '')
            Preferences().set('ip_port', result)
            Menu().createSerialPortsMenu()


class SerialMonitorRunCommand(sublime_plugin.WindowCommand):
    """
    Run a selected serial monitor and show the messages in a new window

    Extends: sublime_plugin.WindowCommand
    """

    def run(self):
        Tools.toggleSerialMonitor(self.window)

    def is_checked(self):
        monitor_module = Serial
        state = False
        serial_port = Preferences().get('id_port', '')
        if serial_port in monitor_module.serials_in_use:
            serial_monitor = monitor_module.serial_monitor_dict.get(
                serial_port)
            if serial_monitor and serial_monitor.isRunning():
                state = True
        return state


class SendMessageSerialCommand(sublime_plugin.WindowCommand):
    """
    Send a text over the selected serial port

    Extends: sublime_plugin.WindowCommand
    """

    def run(self):
        caption = _('send')
        self.window.show_input_panel(caption, '', self.on_done, None, None)

    def on_done(self, text):
        if(text):
            Tools.sendSerialMessage(text)
            self.window.run_command('send_message_serial')


class AutoScrollMonitorCommand(sublime_plugin.WindowCommand):
    """
    The scroll goes automatically to the last line when this option is activated.

    Extends: sublime_plugin.WindowCommand
    """

    def run(self):
        keep = Preferences().get('auto_scroll', False)
        Preferences().set('auto_scroll', not keep)

    def is_checked(self):
        return Preferences().get('auto_scroll', False)


class ChooseBaudrateItemCommand(sublime_plugin.WindowCommand):
    """
    Stores the baudrate selected for the user and save it in
    the preferences file.

    Extends: sublime_plugin.WindowCommand
    """

    def run(self, baudrate_item):
        Preferences().set('baudrate', baudrate_item)

    def is_checked(self, baudrate_item):
        target_baudrate = Preferences().get('baudrate', 9600)
        return baudrate_item == target_baudrate


class ChooseLineEndingItemCommand(sublime_plugin.WindowCommand):
    """
    Stores the Line ending selected for the user and save it in
    the preferences file.

    Extends: sublime_plugin.WindowCommand
    """

    def run(self, line_ending_item):
        Preferences().set('line_ending', line_ending_item)

    def is_checked(self, line_ending_item):
        target_line_ending = Preferences().get('line_ending', '\n')
        return line_ending_item == target_line_ending


class ChooseDisplayModeItemCommand(sublime_plugin.WindowCommand):
    """
    Stores the display mode selected for the user and save it in
    the preferences file.

    Extends: sublime_plugin.WindowCommand
    """

    def run(self, display_mode_item):
        Preferences().set('display_mode', display_mode_item)

    def is_checked(self, display_mode_item):
        target_display_mode = Preferences().get('display_mode', 'Text')
        return display_mode_item == target_display_mode


class UpgradePioCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        view = self.view
        console_name = 'Deviot|Upgrade' + str(time.time())
        console = Console(view.window(), name=console_name)
        PlatformioCLI(view, console, install=True).openInThread('upgrade')


class UpdateBoardListCommand(sublime_plugin.WindowCommand):
    """
    Update the board list, extracting the info from platformIO
    ecosystem

    Extends: sublime_plugin.WindowCommand
    """

    def run(self):
        PlatformioCLI(install=True).openInThread('update_boards')


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


class RemoveUserFilesCommand(sublime_plugin.WindowCommand):

    def run(self):
        confirm = sublime.ok_cancel_dialog(
            _('confirm_del_pref'), _('continue'))

        if(confirm):
            Tools.removePreferences()


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


class OpenBuildFolderCommand(sublime_plugin.TextCommand):
    """
    Open a new window where the user libreries must be installed

    Extends: sublime_plugin.TextCommand
    """

    def run(self, edit):
        temp = Paths.getTempPath()
        url = Paths.getOpenFolderPath(temp)
        sublime.run_command('open_url', {'url': url})


class ChangeBuildFolderCommand(sublime_plugin.WindowCommand):

    def run(self):
        Paths.selectDir(self.window, key='build_dir', func=Preferences().set)


class UseCppTemplate(sublime_plugin.WindowCommand):

    def run(self):
        keep = Preferences().get('use_cpp', False)
        Preferences().set('use_cpp', not keep)

    def is_checked(self):
        return Preferences().get('use_cpp', False)


class SelectLanguageCommand(sublime_plugin.WindowCommand):

    def run(self, id_lang):
        Preferences().set('id_lang', id_lang)

    def is_checked(self, id_lang):
        saved_id_lang = Preferences().get('id_lang')
        return saved_id_lang == id_lang


class DonateDeviotCommand(sublime_plugin.WindowCommand):
    """
    Show the Deviot github site.

    Extends: sublime_plugin.WindowCommand
    """

    def run(self):
        sublime.run_command('open_url', {'url': 'https://goo.gl/LqdDrC'})


class AboutDeviotCommand(sublime_plugin.WindowCommand):
    """
    Show the Deviot github site.

    Extends: sublime_plugin.WindowCommand
    """

    def run(self):
        sublime.run_command('open_url', {'url': 'https://goo.gl/c41EXS'})


class AboutPioCommand(sublime_plugin.WindowCommand):
    """
    Show the Deviot github site.

    Extends: sublime_plugin.WindowCommand
    """

    def run(self):
        sublime.run_command('open_url', {'url': 'http://goo.gl/KiXeZL'})


class AddStatusCommand(sublime_plugin.TextCommand):
    """
    Add a message in the status bar

    Extends: sublime_plugin.TextCommand
    """

    def run(self, edit, text, erase_time):
        Tools.setStatus(self.view, text, erase_time)

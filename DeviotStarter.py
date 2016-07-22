# !/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import os
import sys
import glob
import sublime
import sublime_plugin
import subprocess
import threading
from shutil import rmtree

from .libs import Paths, Tools
from .libs.Menu import Menu
from .libs.PlatformioCLI import PlatformioCLI
from .libs.Preferences import Preferences
from .libs.QuickPanel import quickPanel
from .libs import Libraries
from .libs.I18n import I18n
from .libs import Serial
from .libs import Messages
from .libs.Install import PioInstall
from .libs.Progress import ThreadProgress

_ = I18n().translate

package_name = 'Deviot'


def plugin_loaded():
    window = sublime.active_window()
    thread = threading.Thread(target=PioInstall(window).checkPio)
    thread.start()
    ThreadProgress(thread, _('processing'), _('done'))
    Tools.setStatus()
    Tools.userPreferencesStatus()


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
        PlatformioCLI(feedback=False, console=False).checkInitFile()
        Tools.setStatus()
        Tools.userPreferencesStatus()

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
        keep_cache = Preferences().get('keep_cache', True)
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

    def run(self):
        choose = Menu().createBoardsMenu()
        quickPanel(choose, self.on_done)

    def on_done(self, selected):
        if(selected != -1):
            choose = Menu().createBoardsMenu()
            board_id = choose[selected][1].split(' | ')[1]
            Preferences().boardSelected(board_id)

    def is_enabled(self):
        return Preferences().get('enable_menu', False)


class SelectEnvCommand(sublime_plugin.WindowCommand):
    """
    Stores the environment option selected by the user in
    the preferences files

    Extends: sublime_plugin.WindowCommand
    """

    def run(self):
        list = Menu().getEnvironments()
        quickPanel(list[0],
                   self.on_done, index=list[1])

    def on_done(self, selected):
        list = Menu().getEnvironments()
        if(selected != -1):
            env = list[0][selected][1].split(' | ')[1]
            Tools.saveEnvironment(env)
            Tools.userPreferencesStatus()

    def is_enabled(self):
        return Tools.checkBoards()


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
        quickPanel(choose, self.on_done)

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
        choose = Libraries.Libraries(
            self.window, feedback=False).installedList()
        quickPanel(choose, self.on_done)

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
        PlatformioCLI().openInThread('build')

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
        PlatformioCLI().openInThread('upload')

    def is_enabled(self):
        return Preferences().get('enable_menu')


class CleanSketchCommand(sublime_plugin.TextCommand):
    """
    Trigger a method to delete firmware/program binaries compiled
    if a sketch has been built previously

    Extends: sublime_plugin.TextCommand
    """

    def run(self, edit):
        PlatformioCLI().openInThread('clean')

    def is_enabled(self):
        is_enabled = Preferences().get('enable_menu', False)
        if(is_enabled):
            view = sublime.active_window().active_view()
            is_enabled = Tools.isIOTFile(view.file_name())
        return is_enabled


class OpenIniFileCommand(sublime_plugin.WindowCommand):

    def run(self):
        view = self.window.active_view()
        is_iot = Tools.isIOTFile(view.file_name())

        if(not is_iot):
            return

        views = []
        path = Preferences().get('ini_path', False)
        path = os.path.join(path, 'platformio.ini')
        view = self.window.open_file(path)
        views.append(view)
        if views:
            self.window.focus_view(views[0])

    def is_enabled(self):
        view = self.window.active_view()
        is_iot = Tools.isIOTFile(view.file_name())
        return is_iot


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


class SelectPortCommand(sublime_plugin.WindowCommand):
    """
    Saves the port COM selected by the user in the
    preferences file.

    Extends: sublime_plugin.WindowCommand
    """

    def run(self):
        PlatformioCLI(feedback=False).selectPort()


class ProgrammerNoneCommand(sublime_plugin.WindowCommand):

    def run(self, programmer):
        Preferences().set('programmer', programmer)

    def is_checked(self, programmer):
        prog = Preferences().get('programmer', False)
        return prog == programmer


class ProgrammerAvrCommand(sublime_plugin.WindowCommand):

    def run(self, programmer):
        Preferences().set('programmer', programmer)

    def is_checked(self, programmer):
        prog = Preferences().get('programmer', False)
        return prog == programmer


class ProgrammerAvrMkiiCommand(sublime_plugin.WindowCommand):

    def run(self, programmer):
        Preferences().set('programmer', programmer)

    def is_checked(self, programmer):
        prog = Preferences().get('programmer', False)
        return prog == programmer


class ProgrammerUsbTyniCommand(sublime_plugin.WindowCommand):

    def run(self, programmer):
        Preferences().set('programmer', programmer)

    def is_checked(self, programmer):
        prog = Preferences().get('programmer', False)
        return prog == programmer


class ProgrammerArduinoIspCommand(sublime_plugin.WindowCommand):

    def run(self, programmer):
        Preferences().set('programmer', programmer)

    def is_checked(self, programmer):
        prog = Preferences().get('programmer', False)
        return prog == programmer


class ProgrammerUsbaspCommand(sublime_plugin.WindowCommand):

    def run(self, programmer):
        Preferences().set('programmer', programmer)

    def is_checked(self, programmer):
        prog = Preferences().get('programmer', False)
        return prog == programmer


class ProgrammerParallelCommand(sublime_plugin.WindowCommand):

    def run(self, programmer):
        Preferences().set('programmer', programmer)

    def is_checked(self, programmer):
        prog = Preferences().get('programmer', False)
        return prog == programmer


class ProgrammerArduinoAsIspCommand(sublime_plugin.WindowCommand):

    def run(self, programmer):
        Preferences().set('programmer', programmer)

    def is_checked(self, programmer):
        prog = Preferences().get('programmer', False)
        return prog == programmer


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
        if(not Preferences().get('id_port', False)):
            PlatformioCLI(feedback=False, callback=self.on_done).openInThread(
                'ports', process=False)
            return
        self.on_done()

    def on_done(self):
        Tools.toggleSerialMonitor(self.window)

    def is_checked(self):
        state = False
        monitor_module = Serial
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
        keep = Preferences().get('auto_scroll', True)
        Preferences().set('auto_scroll', not keep)

    def is_checked(self):
        return Preferences().get('auto_scroll', True)


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
        window = sublime.active_window()
        thread = threading.Thread(target=PioInstall(window, True).checkPio)
        thread.start()


class DeveloperPioCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        window = sublime.active_window()
        thread = threading.Thread(target=PioInstall(window, True).developer)
        thread.start()
        ThreadProgress(thread, _('processing'), _('done'))

    def is_checked(self):
        return Preferences().get('developer', False)


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
        keep = Preferences().get('keep_cache', True)
        Preferences().set('keep_cache', not keep)

    def is_checked(self):
        return Preferences().get('keep_cache', True)


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


class UseCppTemplateCommand(sublime_plugin.WindowCommand):

    def run(self):
        keep = Preferences().get('use_cpp', False)
        Preferences().set('use_cpp', not keep)

    def is_checked(self):
        return Preferences().get('use_cpp', False)


class UseAlwaysNativeCommand(sublime_plugin.WindowCommand):

    def run(self):
        keep = Preferences().get('always_native', False)
        Preferences().set('always_native', not keep)

    def is_checked(self):
        return Preferences().get('always_native', False)


class ChangeDefaultPathCommand(sublime_plugin.WindowCommand):
    """
    Set the default path when the "change folder" option is used

    Extends: sublime_plugin.WindowCommand
    """

    def run(self):
        Paths.selectDir(self.window, key='default_path',
                        func=Preferences().set)


class RemoveDefaultPathCommand(sublime_plugin.WindowCommand):
    """
    Remove the default path when the "change folder" option is used

    Extends: sublime_plugin.WindowCommand
    """

    def run(self):
        Preferences().set('default_path', False)


class SelectLanguageCommand(sublime_plugin.WindowCommand):

    def run(self, id_lang):
        restart = sublime.ok_cancel_dialog(_('restart_deviot'),
                                           _('continue_button'))

        if(restart):
            Preferences().set('id_lang', id_lang)
            Preferences().set('updt_menu', True)
            self.window.run_command('sublime_restart')

    def is_checked(self, id_lang):
        saved_id_lang = Preferences().get('id_lang')
        return saved_id_lang == id_lang


class DonateDeviotCommand(sublime_plugin.WindowCommand):
    """
    Show the Deviot github site.

    Extends: sublime_plugin.WindowCommand
    """

    def run(self):
        sublime.run_command('open_url', {'url': 'https://goo.gl/K0EpFU'})


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
        Tools.setStatus(text, erase_time)


class SublimeRestartCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        if(sublime.platform() == 'windows'):
            if sublime.version()[:1] == '3':
                subprocess.call('taskkill /im sublime_text.exe /f && cmd /C "' +
                                os.path.join(os.getcwd(), 'sublime_text.exe') + '"', shell=True)
            else:
                os.execl(sys.executable, ' ')
        elif(sublime.platform() == 'osx'):
            if sublime.version()[:1] == '3':
                subprocess.call("pkill subl && " +
                                os.path.join(os.getcwd(), 'subl'), shell=True)
            else:
                os.execl(os.path.join(os.getcwd(), 'subl'))
        else:
            if sublime.version()[:1] == '3':
                subprocess.call("pkill 'sublime_text' && " +
                                os.path.join(os.getcwd(), 'sublime_text'), shell=True)
            else:
                os.execl(os.path.join(os.getcwd(), 'sublime_text'))

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import os
import time
import json
import threading
import sublime
from re import compile, match

try:
    from collections import OrderedDict
    from .Commands import CommandsPy
    from . import Paths
    from . import Tools
    from .Messages import Console
    from .Messages import MessageQueue
    from .Serial import SerialListener
    from .Serial import listSerialPorts
    from .Preferences import Preferences
    from .JSONFile import JSONFile
    from .Menu import Menu
    from .I18n import I18n
    from .Progress import ThreadProgress
    from . import __version__ as version
    from .Install import PioInstall
except:
    import libs.Paths as Paths
    import libs.Tools as Tools
    from libs.Messages import Console
    from libs.Messages import MessageQueue
    from libs.OrderedDict import OrderedDict
    from libs.Commands import CommandsPy    
    from libs.Serial import SerialListener
    from libs.Serial import listSerialPorts
    from libs.Preferences import Preferences
    from libs.JSONFile import JSONFile
    from libs.Menu import Menu
    from libs.I18n import I18n
    from libs.Progress import ThreadProgress
    from libs import __version__ as version
    from libs.Install import PioInstall

_ = I18n().translate


class PlatformioCLI(CommandsPy):
    '''
    This class handle all the request to the platformio ecosystem.
    From the list of boards to the build/upload of the sketchs.
    More info about platformio in: http://platformio.org/

    Extends: CommandsPy
    '''

    def __init__(self, view=False, console=False, install=False, command=True):
        '''
        Initialize the command and preferences classes, to check
        if the current work file is an IoT type it received the view
        parameter (ST parameter). This parameter is necessary only in
        the options like build or upload.

        Keyword Arguments:
        view {st object} -- stores many info related with ST (default: False)
        '''
        self.Preferences = Preferences()
        self.Menu = Menu()

        # user console
        if(console):
            current_time = time.strftime('%H:%M:%S')
            self.message_queue = MessageQueue(console)
            self.message_queue.startPrint()

        # For installing purposes
        if(install):
            self.Commands = CommandsPy(console=console)
            return

        self.view = view
        self.execute = True
        self.is_native = False
        self.is_iot = False

        if(view):
            # avoid to do anything with a monitor view
            view_name = view.name()
            sketch_size = view.size()
            file_path = Tools.getPathFromView(view)

            if(not file_path and 'monitor' in view_name.lower()):
                try:
                    current_time = time.strftime('%H:%M:%S')
                    self.message_queue.put('invalid_file_{0}', current_time)
                except:
                    pass
                self.execute = False
                return

            # unsaved file
            if(command and not file_path and sketch_size > 0):
                saved_file = self.saveCodeInFile(view)
                view = saved_file[1]
                file_path = Tools.getPathFromView(view)

            if(command and not sketch_size):
                self.message_queue.put('not_empty_sketch_{0}', current_time)

            # current file / view
            current_path = Paths.getCurrentFilePath(view)
            if(not current_path):
                return
            self.is_iot = Tools.isIOTFile(view)
            current_dir = Paths.getCWD(current_path)
            parent_dir = Paths.getParentCWD(current_path)
            file_name = Tools.getFileNameFromPath(file_path)
            temp_name = Tools.getFileNameFromPath(current_path, ext=False)

            if(not self.is_iot):
                self.execute = False

            # check IoT type file
            if(console and not self.is_iot and not self.execute):
                current_time = time.strftime('%H:%M:%S')
                msg = 'not_iot_{0}{1}'
                if(not file_name):
                    msg = 'not_empty_sketch_{0}'
                self.message_queue.put(msg, current_time, file_name)
                self.execute = False
                return

            if(not command and not self.is_iot):
                return

            # Check native project
            for file in os.listdir(parent_dir):
                if(file.endswith('platformio.ini')):
                    self.dir = parent_dir
                    self.src = False
                    self.is_native = True
                    break

            # set native paths
            if(not self.is_native):
                build_dir = self.Preferences.get('build_dir', False)
                if(not build_dir):
                    build_dir = Paths.getTempPath(temp_name)
                self.src = current_dir
                self.dir = build_dir

            # unsaved changes
            if (command and view.is_dirty()):
                view.run_command('save')

            if(console):
                self.message_queue.put(
                    '[ Deviot {0} ] {1}\\n', version, file_name)
                time.sleep(0.02)

            # Initilized commands
            self.Commands = CommandsPy(console=console, cwd=self.dir)

    def checkInitFile(self):
        """
        Check each platformio.ini file and loads the environments already
        initialized.
        """
        protected = self.Preferences.get('protected', False)
        if(not protected):
            return
        # Empy menu if it's not a IoT file
        if(not self.is_iot):
            if(Tools.getPythonVersion() > 2):
                self.Menu.createEnvironmentMenu(empty=True)
            return

        ini_path = Paths.getFullIniPath(self.dir)

        # show non native data
        if(not self.is_native):
            self.Preferences.set('native', False)
            self.Preferences.set('ini_path', self.dir)
            self.Menu.createEnvironmentMenu()
            return
        else:
            self.Preferences.set('native', True)
            self.Preferences.set('ini_path', self.dir)

        # get data from platformio.ini file
        ini_list = []
        with open(ini_path, 'r') as file:
            pattern = compile(r'\[(\w+)\W(\w+)\]')
            for line in file:
                if pattern.findall(line):
                    if('#' not in line):
                        line = match(r"\[\w+:(\w+)\]", line).group(1)
                        ini_list.append(line)

        # save preferences, update menu data
        type = 'board_id' if not self.is_native else 'found_ini'
        self.Preferences.set(type, ini_list)
        self.Menu.createEnvironmentMenu()

    def removeEnvFromFile(self, env):
        """
        Removes the environment select from the platformio.ini file

        Arguments:
            env {string} -- environment to remove
        """
        ini_path = self.Preferences.get('ini_path', False)
        if(not ini_path):
            return

        found = False
        write = False
        buffer = ""

        # exclude environment selected
        ini_path = Paths.getFullIniPath(ini_path)
        if(not os.path.isfile(ini_path)):
            return

        with open(ini_path) as file:
            for line in file:
                if(env in line and not found):
                    found = True
                    write = True
                if(not found):
                    buffer += line
                if(found and line == '\n'):
                    found = False

        # save new platformio.ini
        if(write):
            with open(ini_path, 'w') as file:
                file.write(buffer)

    def overrideSrc(self, ini_path, src_dir):
        """
        Append in the platformio.ini file, the src_dir option
        to override the source folder where the sketch is stored

        Arguments:
            ini_path {string} -- path of the platformio.ini file
            src_dir {string} -- path where source folder the is located
        """
        header = '[platformio]'
        ini_path = Paths.getFullIniPath(self.dir)
        with open(ini_path) as file:
            if header not in file.read():
                with open(ini_path, 'a+') as new_file:
                    new_file.write("\n%s\n" % header)
                    new_file.write("src_dir=%s\n" % src_dir)

    def initSketchProject(self, chosen):
        '''
        command to initialize the board(s) selected by the user. This
        function can only be use if the workig file is an IoT type
        (checked by isIOTFile)
        '''
        # check if it was already initialized
        ini_path = Paths.getFullIniPath(self.dir)
        if(os.path.isfile(ini_path)):
            with open(ini_path) as file:
                if(chosen in file.read()):
                    return

        init_board = '--board=%s ' % chosen

        if(not init_board):
            current_time = time.strftime('%H:%M:%S')
            msg = 'none_board_sel_{0}'
            self.message_queue.put(msg, current_time)
            self.Commands.error_running = True
            return

        command = ['init', '%s' % (init_board)]

        self.Commands.runCommand(command)

        if(not self.Commands.error_running):
            if(self.is_native):
                self.Preferences.set('init_queue', '')
            if(not self.is_native and self.src):
                self.overrideSrc(self.dir, self.src)

    def buildSketchProject(self):
        '''
        Command to build the current working sketch, it must to be IoT
        type (checked by isIOTFile)
        '''
        if(not self.execute):
            self.message_queue.stopPrint()
            return

        # get environment based on the current project
        type = 'env_selected' if not self.is_native else 'native_env_selected'
        choosen_env = self.Preferences.get(type, '')
        if(type == 'native_env_selected' and not choosen_env):
            choosen_env = self.Preferences.get('init_queue', '')

        # check environment selected
        if(not choosen_env):
            current_time = time.strftime('%H:%M:%S')
            self.message_queue.put('none_env_select_{0}', current_time)
            return False

        # initialize the sketch
        self.initSketchProject(choosen_env)

        if(self.Commands.error_running):
            self.message_queue.stopPrint()
            return

        command = ['run', '-e %s' % choosen_env]

        self.Commands.runCommand(command)

        # set build sketch
        if(not self.Commands.error_running):
            self.Preferences.set('builded_sketch', True)
            return choosen_env
        else:
            self.Preferences.set('builded_sketch', False)

    def uploadSketchProject(self):
        '''
        Upload the sketch to the select board to the select COM port
        it returns an error if any com port is selected
        '''
        id_port = self.Preferences.get('id_port', '')
        current_ports = listSerialPorts()

        if(id_port not in current_ports):
            id_port = False

        # check port selected
        if(not id_port):
            current_time = time.strftime('%H:%M:%S')
            self.message_queue.put('none_port_select_{0}', current_time)
            self.execute = False

        if(not self.execute):
            self.message_queue.stopPrint()
            return

        # Stop serial monitor
        Tools.closeSerialMonitors(self.Preferences)

        # Compiling code
        choosen_env = self.buildSketchProject()
        if(not choosen_env):
            return

        if(self.Commands.error_running):
            self.message_queue.stopPrint()
            return

        command = ['run', '-t upload --upload-port %s -e %s' %
                   (id_port, choosen_env)]

        self.Commands.runCommand(command)
        if(not self.Commands.error_running):
            autorun = self.Preferences.get('autorun_monitor', False)
            if(autorun):
                Tools.toggleSerialMonitor()
                self.Preferences.set('autorun_monitor', False)
        self.message_queue.stopPrint()

    def cleanSketchProject(self):
        '''
        Delete compiled object files, libraries and firmware/program binaries
        if a sketch has been built previously
        '''
        if(not self.execute):
            return

        builded_sketch = self.Preferences.get('builded_sketch', '')

        if(not builded_sketch):
            return

        command = ['run', '-t clean']

        self.Commands.runCommand(command)

        if(not self.Commands.error_running):
            self.Preferences.set('builded_sketch', False)
        self.message_queue.stopPrint()

    def openInThread(self, type, chosen=False):
        """
        Opens each action; build/upload/clean in a new thread

        Arguments: type {string} -- type of action.
                   Valid values: build/upload/clean
        """
        if(type == 'init'):
            action_thread = threading.Thread(
                target=self.initSketchProject, args=(chosen,))
            action_thread.start()
        elif(type == 'build'):
            action_thread = threading.Thread(target=self.buildSketchProject)
            action_thread.start()
        elif (type == 'upload'):
            action_thread = threading.Thread(target=self.uploadSketchProject)
            action_thread.start()
        elif(type == 'upgrade'):
            action_thread = threading.Thread(target=PioInstall().checkUpdate)
            action_thread.start()
        elif(type == 'update_boards'):
            action_thread = threading.Thread(target=PlatformioCLI().saveAPIBoards)
            action_thread.start()
        else:
            action_thread = threading.Thread(target=self.cleanSketchProject)
            action_thread.start()
        ThreadProgress(action_thread, _('processing'), _('done'))

    def saveCodeInFile(self, view):
        """
        If the sketch in the current view has been not saved, it generate
        a random name and stores in a temp folder.

        Arguments: view {ST Object} -- Object with multiples options of ST
        """
        ext = '.ino'

        tmp_path = Paths.getTempPath()
        file_name = str(time.time()).split('.')[0]
        file_path = os.path.join(tmp_path, file_name)
        file_path = os.path.join(file_path, 'src')
        os.makedirs(file_path)

        full_path = file_name + ext
        full_path = os.path.join(file_path, full_path)

        region = sublime.Region(0, view.size())
        text = view.substr(region)
        file = JSONFile(full_path)
        file.writeFile(text)

        view.set_scratch(True)
        window = view.window()
        window.run_command('close')
        view = window.open_file(full_path)

        return (True, view)

    def getAPIBoards(self):
        '''
        Get the list of boards from platformIO API using CLI.
        To know more info about platformIO visit:  http://www.platformio.org/

        Returns: {json object} -- list with all boards in a JSON format
        '''
        window = sublime.active_window()
        view = window.active_view()
        Tools.setStatus(view, _('updating_board_list'))

        boards = []
        Run = CommandsPy()

        command = ['boards', '--json-output']
        boards = Run.runCommand(command, setReturn=True)

        Tools.setStatus(view, _('Done'), erase_time=4000)

        return boards

    def saveAPIBoards(self, update_method=False):
        '''
        Save the JSON object in a specific JSON file
        '''
        try:
            from .Menu import Menu
        except:
            from libs.Menu import Menu

        window = sublime.active_window()
        view = window.active_view()
        Tools.setStatus(view, _('updating_board_list'))

        # console
        console_name = 'Deviot|GetBoards' + str(time.time())
        console = Console(window, name=console_name)

        # Queue for the user console
        message_queue = MessageQueue(console)
        message_queue.startPrint()
        message_queue.put("[Deviot {0}]\n", version)
        
        message_queue.put("download_board_list")        
        boards = self.getAPIBoards()

        self.Menu.saveTemplateMenu(
            data=boards, file_name='platformio_boards.json', user_path=True)
        self.saveEnvironmentFile()

        Menu().createMainMenu()
        message_queue.put("list_updated")

    def saveEnvironmentFile(self):
        '''
        Load the JSON file with the list of all boards and re order it
        based on the vendor. after that format the data to operate with
        the standards required for the ST

        Returns: {json array} -- list of all boards to show in the menu
        '''
        boards_list = []

        platformio_data = self.Menu.getTemplateMenu(
            file_name='platformio_boards.json', user_path=True)

        if(not platformio_data):
            return

        platformio_data = json.loads(platformio_data)

        for datakey, datavalue in platformio_data.items():
            # children
            children = {}
            children['caption'] = datavalue['name']
            children['command'] = 'select_env'
            children['checkbox'] = True
            children['args'] = {'board_id': datakey}

            # Board List
            temp_info = {}
            temp_info[datakey] = {'children': []}
            temp_info[datakey]['children'].append(children)
            boards_list.append(temp_info)

        # Save board list
        self.Menu.saveTemplateMenu(
            boards_list, 'env_boards.json', user_path=True)


def generateFiles():
    # Creates new menu
    api_boards = Paths.getTemplateMenuPath('platformio_boards.json',
                                           user_path=True)
    # create main files
    if(not os.path.exists(api_boards)):
        PlatformioCLI().saveAPIBoards()
    Menu().createMainMenu()

    Tools.createCompletions()
    Tools.createSyntaxFile()
    Menu().createLibraryImportMenu()
    Menu().createLibraryExamplesMenu()

    # Run serial port listener
    Serial = SerialListener(func=Menu().createSerialPortsMenu)
    Serial.start()

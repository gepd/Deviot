#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import os
import re
import time
import json
import threading
import sublime

try:
    from collections import OrderedDict
    from .Commands import CommandsPy
    from . import Paths
    from . import Tools
    from .Messages import MessageQueue
    from .Serial import SerialListener
    from .Preferences import Preferences
    from .JSONFile import JSONFile
    from .Menu import Menu
    from .I18n import I18n
    from .Progress import ThreadProgress
except:
    import libs.Paths as Paths
    import libs.Tools as Tools
    from libs.OrderedDict import OrderedDict
    from libs.Commands import CommandsPy
    from libs.Messages import MessageQueue
    from libs.Serial import SerialListener
    from libs.Preferences import Preferences
    from libs.JSONFile import JSONFile
    from libs.Menu import Menu
    from libs.I18n import I18n
    from libs.Progress import ThreadProgress

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
        # For installing purposes
        if(install):
            return

        self.view = view
        self.execute = True
        self.Menu = Menu()
        self.Preferences = Preferences()
        self.env_path = self.Preferences.get('env_path', False)
        self.vbose = self.Preferences.get('verbose_output', False)
        self.is_native = False
        self.is_iot = False

        # user console
        if(console):
            current_time = time.strftime('%H:%M:%S')
            self.message_queue = MessageQueue(console)
            self.message_queue.startPrint()
            self.message_queue.put('[ Deviot ]\\n')

        if(view):
            # current file / view
            current_path = Paths.getCurrentFilePath(view)
            if(not current_path):
                return
            self.is_iot = Tools.isIOTFile(view)
            current_dir = Paths.getCWD(current_path)
            parent_dir = Paths.getParentCWD(current_path)
            sketch_size = view.size()
            file_path = Tools.getPathFromView(view)
            file_name = Tools.getFileNameFromPath(file_path)
            temp_name = Tools.getFileNameFromPath(current_path, ext=False)

            # unsaved file
            if(command and not file_path and sketch_size > 0):
                saved_file = self.saveCodeInFile(view)
                view = saved_file[1]
                file_path = Tools.getPathFromView(view)

            if(not self.is_iot):
                self.execute = False

            # check IoT type file
            if(console and not self.is_iot and not self.execute):
                msg = '{0} {1} is not a IoT File\\n'
                if(not file_name):
                    msg = '{0} Isn\'t possible to upload an empty sketch\\n'
                self.message_queue.put(msg, current_time, file_name)
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
                tmp_path = Paths.getDeviotTmpPath(temp_name)
                self.src = current_dir
                self.dir = tmp_path

            # unsaved changes
            if (command and view.is_dirty()):
                view.run_command('save')

            # Initilized commands
            self.Commands = CommandsPy(
                self.env_path, console=console, cwd=self.dir)

    def checkInitFile(self):

        # Empy menu if it's not a IoT file
        if(not self.is_iot):
            self.Menu.createEnvironmentMenu(empty=True)
            return

        ini_path = Paths.getFullIniPath(self.dir)

        # show non native data
        if(not self.is_native):
            self.Preferences.set('native', False)
            self.Preferences.set('ini_path', self.dir)
            if(not os.path.isfile(ini_path)):
                self.Menu.createEnvironmentMenu()
                return
        else:
            self.Preferences.set('native', True)
            self.Preferences.set('ini_path', self.dir)

        # get data from platformio.ini file
        ini_list = []
        with open(ini_path, 'r') as file:
            pattern = re.compile(r'\[(\w+)\W(\w+)\]')
            for line in file:
                if pattern.findall(line):
                    if('#' not in line):
                        line = re.match(r"\[\w+:(\w+)\]", line).group(1)
                        ini_list.append(line)

        # save preferences, update menu data
        type = 'board_id' if not self.is_native else 'found_ini'
        self.Preferences.set(type, ini_list)
        self.Menu.createEnvironmentMenu()

    def removeEnvFromFile(self, env):
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

    def initSketchProject(self, choosen=None):
        '''
        command to initialize the board(s) selected by the user. This
        function can only be use if the workig file is an IoT type
        (checked by isIOTFile)
        '''
        if(self.is_native):
            choosen = self.Preferences.get('init_queue', False)
            self.dir = self.Preferences.get('ini_path', False)

        # check if it was already initialized
        ini_path = Paths.getFullIniPath(self.dir)
        if(os.path.isfile(ini_path)):
            with open(ini_path) as file:
                if(choosen in file.read()):
                    return

        init_board = '--board=%s ' % choosen

        if(not init_board):
            current_time = time.strftime('%H:%M:%S')
            msg = '{0} None board Selected\\n'
            self.message_queue.put(msg, current_time)
            self.Commands.error_running = True
            return

        command = ['init', '%s' % (init_board)]

        self.Commands.runCommand(command, verbose=self.vbose)

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

        choosen_env = self.Preferences.get('env_selected', False)

        # check environment selected
        if(not choosen_env):
            current_time = time.strftime('%H:%M:%S')
            msg = '{0} None environment selected\\n'
            self.message_queue.put(msg, current_time)
            return

        # initialize the sketch
        self.initSketchProject(choosen_env)

        if(self.Commands.error_running):
            self.message_queue.stopPrint()
            return

        command = ['run', '-e %s' % choosen_env]

        self.Commands.runCommand(command, verbose=self.vbose)

        # set build sketch
        if(not self.Commands.error_running):
            self.Preferences.set('builded_sketch', True)
        else:
            self.Preferences.set('builded_sketch', False)
        self.message_queue.stopPrint()

    def uploadSketchProject(self):
        '''
        Upload the sketch to the select board to the select COM port
        it returns an error if any com port is selected
        '''
        if(not self.execute):
            self.message_queue.stopPrint()
            return

        id_port = self.Preferences.get('id_port', '')
        choosen_env = self.Preferences.get('env_selected', '')

        # check environment selected
        if(not choosen_env):
            current_time = time.strftime('%H:%M:%S')
            msg = '{0} None environment selected\\n'
            self.message_queue.put(msg, current_time)
            return

        # check port selected
        if(not id_port):
            current_time = time.strftime('%H:%M:%S')
            msg = '{0} None serial port selected\\n'
            self.message_queue.put(msg, current_time)
            return

        # Compiling code
        self.buildSketchProject()
        if(self.Commands.error_running):
            self.message_queue.stopPrint()
            return

        command = ['run', '-t upload --upload-port %s -e %s' %
                   (id_port, choosen_env)]

        self.Commands.runCommand(command, verbose=self.vbose)
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

        self.Commands.runCommand(command, verbose=self.vbose)

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
            action_thread = threading.Thread(target=self.initSketchProject)
            action_thread.start()
        elif(type == 'build'):
            action_thread = threading.Thread(target=self.buildSketchProject)
            action_thread.start()
        elif (type == 'upload'):
            action_thread = threading.Thread(target=self.uploadSketchProject)
            action_thread.start()
        else:
            action_thread = threading.Thread(target=self.cleanSketchProject)
            action_thread.start()
        ThreadProgress(action_thread, _('Processing'), _('Done'))

    def saveCodeInFile(self, view):
        """
        If the sketch in the current view has been not saved, it generate
        a random name and stores in a temp folder.

        Arguments: view {ST Object} -- Object with multiples options of ST
        """
        ext = '.ino'

        tmp_path = Paths.getDeviotTmpPath()
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

    def platformioCheck(self):
        '''
        Check if is possible to run a platformIO command
        if isn't, get the env_path value set by the user,
        from the preferences file and tries to run it again
        '''
        # console feedback
        try:
            current_time = time.strftime('%H:%M:%S')
            self.message_queue.put(
                "{0} Checking requirements...\\n", current_time)
        except:
            pass

        # default paths
        if(Tools.getOsName() == 'windows'):
            default_path = ["C:\Python27", "C:\Python27\Scripts"]
        else:
            default_path = ["/usr/bin", "/usr/local/bin"]

        # paths from user preferences file
        user_env_path = self.Preferences.get('env_path', False)
        if(user_env_path):
            for path in reversed(user_env_path.split(os.path.pathsep)):
                if(os.path.isabs(path)):
                    default_path.insert(0, path)

        # Joining system environment paths and default paths
        system_paths = os.environ.get("PATH", "").split(os.path.pathsep)
        for path in system_paths:
            default_path.append(path)
        default_path = list(OrderedDict.fromkeys(default_path))
        env_path = os.path.pathsep.join(default_path)

        command = ['--version']

        Run = CommandsPy(env_path=env_path)
        version = Run.runCommand(command, setReturn=True)
        version = re.sub(r'\D', '', version)
        version = version if version != '' else 0

        if(Run.error_running or version == 0):
            # translate menu
            temp_menu = self.Menu.getTemplateMenu('Install-menu-preset')
            for item in temp_menu[0]['children']:
                item['caption'] = _(item['caption'])
            self.Menu.saveSublimeMenu(temp_menu)

            # console feedback
            try:
                current_time = time.strftime('%H:%M:%S')
                msg = '{0} Platformio is not installed '
                msg += 'or it\'s installed in a custom path.\\n'
                msg += 'Please set your path in the preferences file from '
                msg += 'ST Menu > Deviot > Set Environment PATH'
                self.message_queue.put(msg, current_time)
                time.sleep(0.01)
            except:
                pass

            # Preferences instructions
            if(not user_env_path):
                self.Preferences.set('env_path', _(
                    'SET-YOUR-ENVIRONMENT-PATH'))
            return False

        # Check the minimum version
        if(not Run.error_running and int(version) <= 270):
            # Update menu
            temp_menu = self.Menu.getSublimeMenu()
            status = _('Upgrade PlatformIO')
            temp_menu[0]['children'][0]['caption'] = status
            temp_menu[0]['children'][1] = 0
            temp_menu[0]['children'][3]['caption'] = _("Check again")
            self.Menu.saveSublimeMenu(temp_menu)

            # console feedback
            try:
                current_time = time.strftime('%H:%M:%S')
                msg = '{0} You need to update platformIO'
                self.message_queue.put(msg, current_time)
                time.sleep(0.01)
            except:
                pass

            return False

        # console feedback
        try:
            current_time = time.strftime('%H:%M:%S')
            msg = '{0} PlatformIO has been detected, please wait...\\n'
            self.message_queue.put(msg, current_time)
        except:
            pass

        # save user preferences
        protected = self.Preferences.get('protected', False)
        if(not protected):
            self.Preferences.set('env_path', env_path)
            self.Preferences.set('protected', True)
            self.Preferences.set('enable_menu', True)
            self.env_path = Preferences().get('env_path', False)

        # Creates new menu
        api_boards = Paths.getTemplateMenuPath('platformio_boards.json',
                                               user_path=True)

        if(not os.path.exists(api_boards)):
            self.saveAPIBoards()
        self.Menu.createMainMenu()

        # Run serial port listener
        Serial = SerialListener(func=self.Menu.createSerialPortsMenu)
        Serial.start()

        # console feedback
        try:
            current_time = time.strftime('%H:%M:%S')
            msg = '{0} All done, you can code now!'
            self.message_queue.put(msg, current_time)
        except:
            pass

        return True

    def getAPIBoards(self):
        '''
        Get the list of boards from platformIO API using CLI.
        To know more info about platformIO visit:  http://www.platformio.org/

        Returns: {json object} -- list with all boards in a JSON format
        '''
        boards = []
        Run = CommandsPy(env_path=self.env_path)

        command = ['boards', '--json-output']
        boards = Run.runCommand(command, setReturn=True)
        return boards

    def saveAPIBoards(self, update_method=False):
        '''
        Save the JSON object in a specific JSON file
        '''

        boards = self.getAPIBoards()

        self.Menu.saveTemplateMenu(
            data=boards, file_name='platformio_boards.json', user_path=True)
        self.saveEnvironmentFile()

        if(update_method):
            update_method()

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

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
    from .Commands import CommandsPy
    from . import Paths
    from . import Tools
    from .Messages import MessageQueue
    from .Serial import SerialListener
    from .Preferences import Preferences
    from .JSONFile import JSONFile
    from .Menu import Menu
except:
    import Paths
    import Tools
    from libs.Commands import CommandsPy
    from libs.Messages import MessageQueue
    from libs.Serial import SerialListener
    from libs.Preferences import Preferences
    from libs.JSONFile import JSONFile
    from libs.Menu import Menu


class PlatformioCLI(CommandsPy):
    '''
    This class handle all the request to the platformio ecosystem.
    From the list of boards to the build/upload of the sketchs.
    More info about platformio in: http://platformio.org/

    Extends: CommandsPy
    '''

    def __init__(self, view=False, console=False):
        '''
        Initialize the command and preferences classes, to check
        if the current work file is an IoT type it received the view
        parameter (ST parameter). This parameter is necessary only in
        the options like build or upload.

        Keyword Arguments:
        view {st object} -- stores many info related with ST (default: False)
        '''
        self.execute = True
        self.Preferences = Preferences()
        self.Menu = Menu()
        self.env_path = Preferences().get('env_path', False)

        # user console
        if(console):
            current_time = time.strftime('%H:%M:%S')
            self.message_queue = MessageQueue(console)
            self.message_queue.startPrint()
            self.message_queue.put('[ Deviot ]\\n')

        if(view):
            file_path = Tools.getPathFromView(view)
            file_name = Tools.getFileNameFromPath(file_path)

            # unsaved file
            if(not file_path):
                saved_file = self.saveCodeInFile(view)
                view = saved_file[1]
                file_path = Tools.getPathFromView(view)

            # check IoT type file
            if(not Tools.isIOTFile(view)):
                msg = '{0} {1} is not a IoT File\\n'
                self.message_queue.put(msg, current_time, file_name)
                self.execute = False
                return

            # unsaved changes
            if view.is_dirty():
                view.run_command('save')

            if(self.execute):
                self.flne = Tools.getFileNameFromPath(file_path)
                current_path = Paths.getCurrentFilePath(view)
                current_dir = Paths.getCWD(current_path)
                parent_dir = Paths.getParentCWD(current_path)
                file_name = Tools.getFileNameFromPath(file_path, ext=False)
                tmp_path = Paths.getDeviotTmpPath(file_name)
                # library = Paths.getLibraryPath()

                self.dir = tmp_path
                self.src = current_dir

                # Check initialized project
                for file in os.listdir(parent_dir):
                    if(file.endswith('platformio.ini')):
                        self.dir = parent_dir
                        self.src = False
                        break

                # Initilized commands
                self.Commands = CommandsPy(
                    self.env_path, console=console, cwd=self.dir)

                # user preferences to verbose output
                self.vbose = self.Preferences.get('verbose_output', False)

    def getSelectedBoards(self):
        '''
        Get the board(s) list selected, from the preferences file, to
        be initialized and formated to be used in the platformio CLI

        Returns: {string} boards list in platformio CLI format
        '''
        boards = self.Preferences.get('board_id', '')
        type_boards = ''

        if(not boards):
            return False

        for board in boards:
            type_boards += '--board=%s ' % board

        return type_boards

    def overrideSrc(self, ini_path, src_dir):
        """
        Append in the platformio.ini file, the src_dir option
        to override the source folder where the sketch is stored

        Arguments:
            ini_path {string} -- path of the platformio.ini file
            src_dir {string} -- path where source folder the is located
        """
        ini_path = os.path.join(ini_path, 'platformio.ini')
        header = '[platformio]'

        ini = open(ini_path, 'a+')
        ini.seek(0, 2)
        if header not in ini.read():
            ini.write("\n%s\n" % header)
            ini.write("src_dir=%s" % src_dir)
        ini.close()

    def initSketchProject(self):
        '''
        command to initialize the board(s) selected by the user. This
        function can only be use if the workig file is an IoT type
        (checked by isIOTFile)
        '''
        init_boards = self.getSelectedBoards()

        if(not init_boards):
            current_time = time.strftime('%H:%M:%S')
            msg = '{0} None board Selected\\n'
            self.message_queue.put(msg, current_time)
            self.Commands.error_running = True
            return

        command = ['init', '%s' % (init_boards)]

        self.Commands.runCommand(command, verbose=self.vbose)

        if(not self.Commands.error_running):
            if(self.src):
                self.overrideSrc(self.dir, self.src)

    def buildSketchProject(self):
        '''
        Command to build the current working sketch, it must to be IoT
        type (checked by isIOTFile)
        '''
        if(not self.execute):
            self.message_queue.stopPrint()
            return

        # initialize the sketch
        self.initSketchProject()

        if(self.Commands.error_running):
            self.message_queue.stopPrint()
            return

        command = ['run']

        self.Commands.runCommand(command, verbose=self.vbose)

        # set
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

        # Compiling code
        self.buildSketchProject()
        if(self.Commands.error_running):
            self.message_queue.stopPrint()
            return

        id_port = self.Preferences.get('id_port', '')
        env_sel = self.Preferences.get('env_selected', '')

        # check port selected
        if(not id_port):
            current_time = time.strftime('%H:%M:%S')
            msg = '{0} None serial port selected\\n'
            self.message_queue.put(msg, current_time)
            return

        # check environment selected
        if(not env_sel):
            current_time = time.strftime('%H:%M:%S')
            msg = '{0} None environment selected\\n'
            self.message_queue.put(msg, current_time)
            return

        command = ['run', '-t upload --upload-port %s -e %s' %
                   (id_port, env_sel)]

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

    def openInThread(self, type):
        """
        Opens each action; build/upload/clean in a new thread

        Arguments: type {string} -- type of action.
                   Valid values: build/upload/clean
        """
        if(type == 'build'):
            action_thread = threading.Thread(target=self.buildSketchProject)
            action_thread.start()
        elif (type == 'upload'):
            action_thread = threading.Thread(target=self.uploadSketchProject)
            action_thread.start()
        else:
            action_thread = threading.Thread(target=self.cleanSketchProject)
            action_thread.start()

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
        # default paths
        if(Tools.getOsName() == 'windows'):
            default_path = ["C:\Python27", "C:\Python27\Scripts"]
        else:
            default_path = ["/usr/bin", "/usr/local/bin"]

        # paths from user preferences file
        user_env_path = self.Preferences.get('env_path', '')
        if(user_env_path):
            default_path += [path for path in user_env_path.split(
                os.path.pathsep)]

        # join all paths
        default_path = set(default_path)
        env_path = os.path.pathsep.join(list(default_path | set(
            os.environ.get("PATH", "").split(os.path.pathsep))))

        command = ['--version']

        Run = CommandsPy(env_path=env_path)
        version = Run.runCommand(command, setReturn=True)
        version = re.sub(r'\D', '', version)

        if(Run.error_running):
            return False

        # Check the minimum version
        if(not Run.error_running and int(version) < 270):
            self.Preferences.set('enable_menu', False)
            temp_menu = self.Menu.getSublimeMenu()

            temp_menu[0]['children'][0][
                'caption'] = 'Please upgrade Platformio'
            temp_menu[0]['children'][1] = 0

            self.Menu.saveSublimeMenu(temp_menu)
            return False

        # save user preferences
        self.Preferences.set('env_path', env_path)
        self.Preferences.set('enable_menu', True)

        # Creates new menu
        api_boards = Paths.getTemplateMenuPath('platformio_boards.json',
                                               user_path=True)

        if(not os.path.exists(api_boards)):
            self.saveAPIBoards()
        self.Menu.createMainMenu()

        # Run serial port listener
        Serial = SerialListener(func=self.Menu.createSerialPortsMenu)
        Serial.start()

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

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import os
import re
import time
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
    '''Platformio

    This class handle all the request to the platformio ecosystem.
    From the list of boards to the build/upload of the sketchs.
    More info about platformio in: http://platformio.org/

    Extends:
            CommandsPy
    '''

    def __init__(self, view=False, console=False):
        '''Construct

        Initialize the command and preferences classes, to check
        if the current work file is an IoT type it received the view
        parameter (ST parameter). This parameter is necessary only in
        the options like build or upload.

        Keyword Arguments:
                view {st object} -- stores many info related with
                                                        ST (default: False)
        '''
        self.execute = True
        self.Preferences = Preferences()

        # user console
        if(console):
            current_time = time.strftime('%H:%M:%S')
            self.message_queue = MessageQueue(console)
            self.message_queue.startPrint()
            self.message_queue.put('[ Deviot ]\n')

        if(view):
            file_path = Tools.getPathFromView(view)
            file_name = Tools.getFileNameFromPath(file_path)

            # unsaved file
            if(not file_path):
                saved_file = self.saveFile(view)
                if(saved_file[1]):
                    view = saved_file[1]

            # check IoT type file
            if(not Tools.isIOTFile(view)):
                msg = '%s %s is not a IoT File\n' % (current_time, file_name)
                self.message_queue.put(msg)
                self.execute = False
                return

            # unsaved changes
            if view.is_dirty():
                view.run_command('save')

            if(self.execute):
                current_file_path = Paths.getCurrentFilePath(view)
                current_dir = Paths.getCWD(current_file_path)
                parent_dir = Paths.getParentCWD(current_file_path)
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
            env_path = self.Preferences.get('env_path', False)
            self.Commands = CommandsPy(env_path,
                                       console=console,
                                       cwd=self.dir)

        # Preferences
        self.vbose = self.Preferences.get('verbose_output', False)

    def getSelectedBoards(self):
        '''Selected Board(s)

        Get the board(s) list selected, from the preferences file, to
        be initialized and formated to be used in the platformio CLI

        Returns:
                {string} boards list in platformio CLI format
        '''
        boards = self.Preferences.get('board_id', '')
        type_boards = ''

        if(not boards):
            return False

        for board in boards:
            type_boards += '--board=%s ' % board

        return type_boards

    def overrideSrc(self, ini_path, src_dir):
        ini_path = os.path.join(ini_path, 'platformio.ini')
        header = '[platformio]'

        ini = open(ini_path, 'a+')
        ini.seek(0, 2)
        if header not in ini.read():
            ini.write("\n%s\n" % header)
            ini.write("src_dir=%s" % src_dir)
        ini.close()

    def initSketchProject(self):
        '''CLI

        command to initialize the board(s) selected by the user. This
        function can only be use if the workig file is an IoT type
        (checked by isIOTFile)
        '''
        init_boards = self.getSelectedBoards()

        if(not init_boards):
            current_time = time.strftime('%H:%M:%S')
            msg = '%s None board Selected\n' % current_time
            self.message_queue.put(msg)
            self.Commands.error_running = True
            return

        command = ['init', '%s' % (init_boards)]

        self.start_time = time.time()
        current_time = time.strftime('%H:%M:%S')
        msg = '%s Initializing the project | ' % current_time

        self.message_queue.put(msg)
        self.Commands.runCommand(command, verbose=self.vbose)

        if(not self.Commands.error_running):
            msg = 'Success\n'
            self.message_queue.put(msg)
            if(self.src):
                self.overrideSrc(self.dir, self.src)
        else:
            msg = 'Error\n'
            self.message_queue.put(msg)

    def buildSketchProject(self):
        '''CLI

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

        current_time = time.strftime('%H:%M:%S')
        msg = '%s Building the project | ' % current_time
        self.message_queue.put(msg)

        command = ['run']

        self.Commands.runCommand(command, verbose=self.vbose)

        if(not self.Commands.error_running):
            current_time = time.strftime('%H:%M:%S')
            diff_time = time.time() - self.start_time
            msg = 'Success\n%s it took %ds\n' % (current_time, diff_time)

            self.message_queue.put(msg)
            self.Preferences.set('builded_sketch', True)
        else:
            current_time = time.strftime('%H:%M:%S')
            msg = 'Error\n%s an error occurred\n' % current_time

            self.message_queue.put(msg)
            self.Preferences.set('builded_sketch', False)
        self.message_queue.stopPrint()

    def uploadSketchProject(self):
        '''CLI

        Upload the sketch to the select board to the select COM port
        it returns an error if any com port is selected
        '''
        if(not self.execute):
            self.message_queue.stopPrint()
            return

        builded_sketch = self.Preferences.get('builded_sketch', '')

        if(not builded_sketch):
            return

        id_port = self.Preferences.get('id_port', '')
        env_sel = self.Preferences.get('env_selected', '')

        if(not id_port):
            current_time = time.strftime('%H:%M:%S')
            msg = '%s None COM port selected\n' % current_time
            self.message_queue.put(msg)
            return

        if(not env_sel):
            current_time = time.strftime('%H:%M:%S')
            msg = '%s None environment selected\n' % current_time
            self.message_queue.put(msg)
            return

        start_time = time.time()
        current_time = time.strftime('%H:%M:%S')
        msg = '%s Uploading firmware | ' % current_time
        self.message_queue.put(msg)

        command = ['run', '-t upload --upload-port %s -e %s' %
                   (id_port, env_sel)]

        self.Commands.runCommand(command, verbose=self.vbose)

        if(not self.Commands.error_running):
            current_time = time.strftime('%H:%M:%S')
            diff_time = time.time() - start_time
            msg = 'success\n%s it took %ds\n' % (current_time, diff_time)

            self.message_queue.put(msg)
            self.Preferences.set('builded_sketch', True)
        else:
            current_time = time.strftime('%H:%M:%S')
            msg = 'Error\n%s an error occurred\n' % current_time

            self.message_queue.put(msg)
            self.Preferences.set('builded_sketch', False)
        self.message_queue.stopPrint()

    def cleanSketchProject(self):
        '''CLI

        Delete compiled object files, libraries and firmware/program binaries
        if a sketch has been built previously
        '''
        if(not self.execute):
            self.message_queue.stopPrint()
            return

        builded_sketch = self.Preferences.get('builded_sketch', '')

        if(not builded_sketch):
            return

        start_time = time.time()
        current_time = time.strftime('%H:%M:%S')
        msg = '%s Cleaning built files | ' % current_time
        self.message_queue.put(msg)

        command = ['run', '-t clean']

        self.Commands.runCommand(command, verbose=self.vbose)

        if(not self.Commands.error_running):
            current_time = time.strftime('%H:%M:%S')
            diff_time = time.time() - start_time
            msg = 'Success\n%s it took %ds\n' % (current_time, diff_time)

            self.message_queue.put(msg)
            self.Preferences.set('builded_sketch', False)
        else:
            current_time = time.strftime('%H:%M:%S')
            msg = '%s Error cleaning files\n' % current_time

            self.message_queue.put(msg)

    def openInThread(self, type):
        if(type == 'build'):
            action_thread = threading.Thread(target=self.buildSketchProject)
            action_thread.start()
        elif (type == 'upload'):
            action_thread = threading.Thread(target=self.uploadSketchProject)
            action_thread.start()
        else:
            action_thread = threading.Thread(target=self.cleanSketchProject)
            action_thread.start()

    def getAPIBoards(self):
        '''Get boards list

        Get the boards list from the platformio API using CLI.
        to know more about platformio visit:  http://www.platformio.org/

        Returns:
                {json object} -- list with all boards in a JSON format
        '''
        boards = []
        command = ['boards', '--json-output']

        boards = self.Commands.runCommand(command, setReturn=True)
        return boards

    def saveFile(self, view):
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
        '''Platformio
        Check if is possible to run a platformio command
        if can't check for the preferences file,

        '''
        env_path = self.Preferences.get('env_path', False)

        command = ['--version']

        Run = CommandsPy(env_path=env_path)
        version = Run.runCommand(command, setReturn=True)
        version = re.sub(r'\D', '', version)

        # Check the minimum version
        if(not Run.error_running and int(version) < 270):
            self.Preferences.set('enable_menu', False)
            temp_menu = Menu().getSublimeMenu()

            temp_menu[0]['children'][0][
                'caption'] = 'Please upgrade Platformio'
            temp_menu[0]['children'][1] = 0

            Menu().saveSublimeMenu(temp_menu)
            return False

        # Check if the environment path is set in preferences file
        if(Run.error_running):
            self.Preferences.set('enable_menu', False)

            if(not env_path):
                # Create prefences file
                self.Preferences.set('env_path', 'YOUR-ENVIRONMENT-PATH-HERE')
            return False

        env_path = self.Preferences.get('env_path', False)

        # Set env path to False if it wasn't assigned
        if(env_path == 'YOUR-ENVIRONMENT-PATH-HERE'):
            self.Preferences.set('env_path', False)

        self.Preferences.set('enable_menu', True)

        # Creates new menu
        api_boards = Paths.getTemplateMenuPath('platformio_boards.json',
                                               user_path=True)

        if(not os.path.exists(api_boards)):
            Menu().saveAPIBoards(self.getAPIBoards)
        Menu().createMainMenu()

        # Run serial port listener
        Serial = SerialListener(func=Menu().createSerialPortsMenu)
        Serial.start()

        return True

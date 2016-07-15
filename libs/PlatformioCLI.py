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
    from .Commands import CommandsPy
    from . import Paths
    from . import Tools
    from .Messages import Console
    from .Messages import MessageQueue
    from .Preferences import Preferences
    from .JSONFile import JSONFile
    from .Menu import Menu
    from .I18n import I18n
    from .Progress import ThreadProgress
    from . import __version__ as version
    from .Install import PioInstall
    from .QuickPanel import quickPanel
except:
    import libs.Paths as Paths
    import libs.Tools as Tools
    from libs.Messages import Console
    from libs.Messages import MessageQueue
    from libs.Commands import CommandsPy
    from libs.Preferences import Preferences
    from libs.JSONFile import JSONFile
    from libs.Menu import Menu
    from libs.I18n import I18n
    from libs.Progress import ThreadProgress
    from libs import __version__ as version
    from libs.Install import PioInstall
    from libs.QuickPanel import quickPanel

_ = I18n().translate


class PlatformioCLI(CommandsPy):
    '''
    This class handle all the request to the platformio ecosystem.
    From the list of boards to the build/upload of the sketchs.
    More info about platformio in: http://platformio.org/

    Extends: CommandsPy
    '''

    def __init__(self, feedback=True):
        self.window = sublime.active_window()
        self.ports_list = []
        self.built = False
        self.process = True
        console = Console(name='Deviot|%s' % (str(time.time())))
        current_time = time.strftime('%H:%M:%S')
        view = self.window.active_view()
        view_name = view.name()
        sketch_size = view.size()
        file_path = view.file_name()
        temp_name = Tools.getFileNameFromPath(file_path, ext=False)
        file_name = Tools.getFileNameFromPath(file_path)
        self.is_iot = Tools.isIOTFile(file_path)

        # cancel feedback if quick panel will be used
        if(self.is_iot):
            if(not Tools.checkBoards() or
               not Tools.checkEnvironments() or
               not Preferences().get('id_port', False)):
                feedback = False

        # header for deviot
        if(feedback):
            if(not file_name):
                file_name = ""
            self.message_queue = MessageQueue(console)
            self.message_queue.startPrint()
            self.message_queue.put('[ Deviot {0} ] {1}\\n', version, file_name)

        # avoid to do anything with a monitor view
        if(feedback and not file_path and 'monitor' in view_name.lower()):
            self.message_queue.put('invalid_file_{0}', current_time)
            return

        # unsaved file
        if(feedback and not sketch_size):
            self.message_queue.put('not_empty_sketch_{0}', current_time)
            self.built = False
            return

        # stop if nothing to process and show
        if(not feedback and not self.is_iot):
            return

        # unsaved changes
        if (view.is_dirty()):
            view.run_command('save')

        # save file not empty
        if(not file_path and sketch_size > 0):
            saved_file = self.saveCodeInFile(view)
            view = saved_file[1]
            file_path = Tools.getPathFromView(view)

        self.current_path = Paths.getCWD(file_path)
        parent_path = Paths.getParentPath(file_path)

        # check if file is iot
        if(feedback and not self.is_iot):
            self.message_queue.put('not_iot_{0}{1}', current_time, file_name)
            return

        # Check native project
        self.is_native = False
        for file in os.listdir(parent_path):
            if(file.endswith('platformio.ini')):
                self.is_native = True
                self.project_dir = parent_path
                break

        # set not native paths
        if(not self.is_native):
            self.project_dir = Paths.getBuildPath(temp_name)
            if(not self.project_dir):
                self.project_dir = Paths.getTempPath(temp_name)
            type_env = 'env_selected'
        else:
            type_env = 'native_env_selected'

        self.ini_path = os.path.join(self.project_dir, 'platformio.ini')
        self.environment = Preferences().get(type_env, False)
        self.Commands = CommandsPy(console=console, cwd=self.project_dir)

    def checkInitFile(self):
        """
        Check each platformio.ini file and loads the environments already
        initialized.
        """
        protected = Preferences().get('protected', False)
        if(not protected):
            return
        # Empy menu if it's not a IoT file
        if(not self.is_iot):
            return

        # show non native data
        if(not self.is_native):
            Preferences().set('native', False)
            Preferences().set('ini_path', self.project_dir)
            return
        else:
            Preferences().set('native', True)
            Preferences().set('ini_path', self.project_dir)

        # get data from platformio.ini file
        ini_list = []
        with open(self.ini_path, 'r') as file:
            pattern = compile(r'\[(\w+)\W(\w+)\]')
            for line in file:
                if pattern.findall(line):
                    if('#' not in line):
                        line = match(r"\[\w+:(\w+)\]", line).group(1)
                        ini_list.append(line)

        # save preferences, update menu data
        type = 'board_id' if not self.is_native else 'found_ini'
        Preferences().set(type, ini_list)

    def beforeProcess(self, next):
        if(not self.is_iot):
            return

        if(next):
            Preferences().set('next', next)
        # if none board is selected show a quick panel list
        if(not Tools.checkBoards()):
            choose = Menu().createBoardsMenu()
            quickPanel(choose, self.saveBoard)
            return

        # if none environment is selected show a quick panel list
        if(not Tools.checkEnvironments()):
            list = Menu().getEnvironments()
            quickPanel(list[0], self.saveEnvironmet, index=list[1])
            return

        # check if the port is available
        id_port = Preferences().get('id_port', '')
        if(next == 'upload' and not any(id_port in port for port in self.ports_list)):
            self.openInThread('ports')
            return

        self.openInThread(next)

    def selectPort(self, process=True):
        self.process = process
        self.ports_list = self.listSerialPorts()

        list = self.ports_list
        quickPanel(list, self.savePort)

    def saveBoard(self, selected):
        if(selected != -1):
            choose = Menu().createBoardsMenu()
            board_id = choose[selected][1].split(' | ')[1]
            Preferences().boardSelected(board_id)
            Tools.saveEnvironment(board_id)
            Tools.userPreferencesStatus()
            next = Preferences().get('next')
            self.beforeProcess(next)

    def saveEnvironmet(self, selected):
        if(selected != -1):
            list = Menu().getEnvironments()
            env = list[0][selected][1].split(' | ')[1]
            Tools.saveEnvironment(env)
            Tools.userPreferencesStatus()
            self.environment = env
            next = Preferences().get('next')
            self.beforeProcess(next)

    def savePort(self, selected):
        if(selected != -1):
            choose = self.ports_list
            id_port = choose[selected][0]
            self.port = id_port
            Preferences().set('id_port', id_port)
            if(self.process):
                next = Preferences().get('next')
                self.beforeProcess(next)

    def initProject(self):
        # check if it was already initialized
        if(os.path.isfile(self.ini_path)):
            with open(self.ini_path) as file:
                if(self.environment in file.read()):
                    return

        command = ['init', '--board=%s' % (self.environment)]

        self.Commands.runCommand(command, "init_project_{0}")

        if(not self.Commands.error_running):
            if(self.is_native):
                Preferences().set('init_queue', '')
            if(not self.is_native):
                self.overrideSrc()

    def overrideSrc(self):
        """
        Append in the platformio.ini file, the src_dir option
        to override the source folder where the sketch is stored

        Arguments:
            ini_path {string} -- path of the platformio.ini file
            src_dir {string} -- path where source folder the is located
        """
        header = '[platformio]'
        with open(self.ini_path) as file:
            if header not in file.read():
                with open(self.ini_path, 'a+') as new_file:
                    new_file.write("\n%s\n" % header)
                    new_file.write("src_dir=%s\n" % self.current_path)

    def programmer(self, programmer):
        # list of programmers
        if(programmer == "avr"):  # AVR ISP
            programmer_string = \
                "#\nupload_protocol = stk500v1\n" \
                "upload_flags = -P$UPLOAD_PORT\n\n" \
                "upload_port = %s\n#\n" % (self.port)
        elif(programmer == "avrmkii"):  # AVRISP mkII
            programmer_string = \
                "#\nupload_protocol = stk500v2\n"\
                "upload_flags = -Pusb\n#\n"
        elif(programmer == "usbtyni"):  # USBtinyISP
            programmer_string = "#\nupload_protocol = usbtiny\n#\n"
        elif(programmer == "arduinoisp"):  # ArduinoISP
            programmer_string = "#\nupload_protocol = arduinoisp\n#\n"
        elif(programmer == "usbasp"):  # USBasp
            programmer_string = "#\nupload_protocol = usbasp\n" \
                "upload_flags = -Pusb\n#\n"
        elif(programmer == "parallel"):  # Parallel Programmer
            programmer_string = "#\nupload_protocol = dapa\n" \
                "upload_flags = -F\n#\n"
        elif(programmer == "arduinoasisp"):  # Arduino as ISP
            programmer_string = "#\nupload_protocol = stk500v1\n" \
                "upload_flags = -P$UPLOAD_PORT -b$UPLOAD_SPEED\n" \
                "upload_speed = 19200\n" \
                "upload_port = %s\n#\n" % (self.port)
        else:
            programmer_string = False

        found = False
        pound = False
        clean = True
        header_env = str.encode("[env:%s]" % self.environment)
        temp = os.path.join(self.project_dir, "temp")

        # searching programmer lines
        if(programmer_string):
            with open(self.ini_path, 'r') as file:
                if 'upload_protocol =' in file.read():
                    clean = False

        # writing lines
        with open(self.ini_path, 'rb') as file, open(temp, 'wb') as new_file:
            for line in file:
                if(pound and b'#' in line):
                    pound = -1
                if(header_env in line):
                    found = True
                if(found and pound != -1 and b'#' in line):
                    pound = True
                if(programmer_string and pound == -1 and b'\n' == line):
                    new_file.write(str.encode(programmer_string))
                    found = False
                if(found and clean and programmer_string and line == b'\n'):
                    new_file.write(str.encode(programmer_string))
                if(not pound or pound == -1 and b'#' not in line):
                    new_file.write(line)

        if(sublime.platform() == 'windows'):
            os.remove(self.ini_path)  # For windows only
        os.rename(temp, self.ini_path)  # Rename the new file

    def build(self):
        if(not self.is_iot):
            return

        # initialize the sketch
        self.initProject()

        # stop if there is an error
        if(self.Commands.error_running):
            return

        command = ['run', '-e %s' % self.environment]
        self.Commands.runCommand(command, "built_project_{0}")

        self.built = True
        if(self.Commands.error_running):
            self.built = False

    def upload(self):
        if(not self.is_iot):
            return

        # Stop serial monitor
        Tools.closeSerialMonitors(Preferences())

        # Compile code
        self.build()

        # stop if there is an error
        if(self.Commands.error_running):
            self.message_queue.stopPrint()
            return

        # check programmer
        programmer = Preferences().get("programmer", False)
        if(not programmer):
            command = ['run', '-t', 'upload', '--upload-port %s -e %s' %
                       (self.port, self.environment)]
        else:
            command = ['run', '-t', 'program']

        self.programmer(programmer)

        # run command
        self.Commands.runCommand(command, "uploading_firmware_{0}")

        # start the monitor serial if was running previously
        if(not self.Commands.error_running):
            autorun = Preferences().get('autorun_monitor', False)
            if(autorun):
                Tools.toggleSerialMonitor()
                Preferences().set('autorun_monitor', False)
        self.message_queue.stopPrint()

    def clean(self):
        if(not self.is_iot):
            return

        command = ['run', '-t clean']
        self.Commands.runCommand(command, "clean_built_files__{0}")

    def openInThread(self, type, process=True):
        """
        Opens each action; build/upload/clean in a new thread

        Arguments: type {string} -- type of action.
                   Valid values: build/upload/clean
        """
        if(type == 'build'):
            action_thread = threading.Thread(target=self.build)
            action_thread.start()
        elif (type == 'upload'):
            action_thread = threading.Thread(target=self.upload)
            action_thread.start()
        elif(type == 'upgrade'):
            feedback = False
            action_thread = threading.Thread(
                target=PioInstall().checkPio, args=(feedback,))
            action_thread.start()
        elif(type == 'ports'):
            action_thread = threading.Thread(
                target=self.selectPort, args=(process,))
            action_thread.start()
        else:
            action_thread = threading.Thread(target=self.clean)
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

    def listSerialPorts(self):
        Run = CommandsPy()

        list = [[_('select_port_list')]]
        command = ['serialports', 'list', '--json-output']

        serial = Run.runCommand(command, setReturn=True)
        serial = json.loads(serial)

        for port in serial:
            list.append([port['port']])

        return list

    def getAPIBoards(self):
        '''
        Get the list of boards from platformIO API using CLI.
        To know more info about platformIO visit:  http://www.platformio.org/

        Returns: {json object} -- list with all boards in a JSON format
        '''
        Tools.setStatus(_('updating_board_list'))

        boards = []
        Run = CommandsPy()

        command = ['boards', '--json-output']
        boards = Run.runCommand(command, setReturn=True)

        Tools.setStatus(_('Done'), erase_time=4000)

        Menu().saveTemplateMenu(
            data=boards, file_name='platformio_boards.json', user_path=True)


def generateFiles():
    # create main files
    PlatformioCLI(feedback=False).getAPIBoards()
    Menu().createMainMenu()

    Tools.createCompletions()
    Tools.createSyntaxFile()
    Menu().createLibraryImportMenu()
    Menu().createLibraryExamplesMenu()

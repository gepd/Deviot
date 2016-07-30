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
from shutil import move

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
from .QuickPanel import quickPanel

_ = I18n().translate


class PlatformioCLI(CommandsPy):
    '''
    This class handle all the request to the platformio ecosystem.
    From the list of boards to the build/upload of the sketchs.
    More info about platformio in: http://platformio.org/

    Extends: CommandsPy
    '''

    def __init__(self, feedback=True, console=True):
        self.window = sublime.active_window()
        self.view = self.window.active_view()
        self.file_path = self.view.file_name()
        self.sketch_size = self.view.size()
        self.view_name = self.view.name()
        self.temp_name = Tools.getFileNameFromPath(self.file_path, ext=False)
        self.file_name = Tools.getFileNameFromPath(self.file_path)
        self.is_iot = Tools.isIOTFile(self.file_path)
        self.current_time = time.strftime('%H:%M:%S')
        self.port = Preferences().get('id_port', '')
        self.feedback = feedback
        self.project_dir = None
        self.environment = None
        self.console = console
        self.init_path = None
        self.Commands = None
        self.callback = None
        self.ports_list = []
        self.sel_index = 0
        self.built = False
        self.auth = False

    def loadData(self):
        """File info

        Get and process data from the current file, if the file is
        being processing, shows errors or information in the user console
        """
        # cancel feedback if quick panel will be used
        if(self.is_iot):
            if(not Tools.checkBoards() or
               not Tools.checkEnvironments() or
               not Preferences().get('id_port', False)):
                self.feedback = False

        # avoid to do anything with a monitor view
        if(self.feedback and not self.file_path and 'monitor' in self.view_name.lower()):
            console = Console(self.window)
            self.message_queue = MessageQueue(console)
            self.message_queue.startPrint()
            self.message_queue.put('_deviot_{0}', version)
            self.message_queue.put('invalid_file_{0}', self.current_time)
            return

        # empty sketch
        if(self.feedback and not self.sketch_size):
            console = Console(self.window)
            self.message_queue = MessageQueue(console)
            self.message_queue.startPrint()
            self.message_queue.put('_deviot_{0}', version)
            self.message_queue.put('not_empty_sketch_{0}', self.current_time)
            self.built = False
            return

        # stop if nothing to process and show
        if(not self.feedback and not self.is_iot):
            return

        # save file not empty
        if(not self.file_path and self.sketch_size > 0):
            saved_file = self.saveCodeInFile(self.view)
            self.view = saved_file[1]
            self.file_path = Tools.getPathFromView(self.view)
            self.file_name = Tools.getFileNameFromPath(self.file_path)
            self.temp_name = Tools.getFileNameFromPath(self.file_path,
                                                       ext=False)
            self.is_iot = Tools.isIOTFile(self.file_path)

        # check if file is iot
        if(self.feedback and not self.is_iot):
            console = Console(self.window)
            self.message_queue = MessageQueue(console)
            self.message_queue.startPrint()
            self.message_queue.put('_deviot_{0}', version)
            self.message_queue.put('not_iot_{0}{1}', self.current_time,
                                   self.file_name)
            return

        # unsaved changes
        if (self.view.is_dirty()):
            self.view.run_command('save')

        self.current_path = Paths.getCWD(self.file_path)
        self.parent_path = Paths.getParentPath(self.file_path)

        if("Temp" in self.file_path or "tmp" in self.file_path):
            self.is_native = True
        else:
            # Check native project
            self.is_native = False
            for file in os.listdir(self.parent_path):
                if(file.endswith('platformio.ini')):
                    self.is_native = True
                    break

        # set not native paths
        if(not self.is_native):
            self.project_dir = Paths.getBuildPath(self.temp_name)
            if(not self.project_dir):
                self.project_dir = Paths.getTempPath(self.temp_name)
            type_env = 'env_selected'
            # save in preferences
            Preferences().set('ini_path', self.project_dir)
            Preferences().set('native', False)
        else:
            self.project_dir = self.parent_path
            type_env = 'native_env_selected'
            # save in preferences
            Preferences().set('ini_path', self.project_dir)
            Preferences().set('native', True)

        self.ini_path = os.path.join(self.project_dir, 'platformio.ini')
        self.environment = Preferences().get(type_env, False)

    def checkInitFile(self):
        """
        Check each platformio.ini file and loads the environments already
        initialized.
        """
        self.loadData()

        protected = Preferences().get('protected', False)
        if(not protected):
            return
        # stop if it's not a IoT file
        if(not self.is_iot):
            return

        # force to create native projects
        if(Preferences().get('always_native', False)):
            self.is_native = True
            Preferences().set('native', True)

        # only if platformio.ini exist
        if(not self.ini_path):
            return

        # check if ini file exists
        if(not os.path.isfile(self.ini_path)):
            return

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

        if(self.is_native):
            current = Preferences().get(type, ini_list)
            ini_list.extend(current)
            ini_list = list(set(ini_list))

        Preferences().set(type, ini_list)

    def beforeProcess(self, next):
        """Requierements

        Check if all the requirements are met based in the type of command. If
        it's necessary shows the quick panel to choose an option

        Arguments:
            next {str} -- name of the next method to call
        """
        self.loadData()

        if(not self.is_iot):
            return

        if(not self.callback):
            self.callback = next

        # if none board is selected show a quick panel list
        if(not Tools.checkBoards()):
            choose = Menu().createBoardsMenu()
            quickPanel(choose, self.saveBoardCallback)
            return

        # if none environment is selected show a quick panel list
        if(not Tools.checkEnvironments()):
            list = Menu().getEnvironments()
            quickPanel(list[0], self.saveEnvironmetCallback, index=list[1])
            return

        if(next == 'upload' and not self.ports_list):
            self.openInThread(self.listSerialPorts)
            return

        # check if the port is available
        if(next == 'upload' and not any(x in self.port for x in self.ports_list[0]) or self.port == ''):
            self.openInThread(self.selectPort)
            return

        mcu = self.getMCU()
        if(next == 'upload' and "esp" in mcu and "COM" not in self.port):
            # check if auth is required to mdns
            from . import Serial
            saved_auth = Preferences().get('auth', False)
            mdns = Serial.listMdnsServices()

            for service in mdns:
                try:
                    service = json.loads(service)
                    server = service['server']
                    if(server[:-1] == self.port):
                        auth = service["properties"]["auth_upload"]
                        self.auth = True if auth == 'yes' else False
                except:
                    pass

            # check if auth is required
            if(self.auth):
                if(not saved_auth or saved_auth == '0' and self.mDNSCheck()):
                    self.window.show_input_panel(_("pass_caption"), '',
                                                 self.saveAuthPassword, None, None)
                return

        try:
            if(self.console):
                self.console = Console(self.window)
            self.Commands = CommandsPy(console=self.console,
                                       cwd=self.project_dir)
        except:
            pass

        if(self.callback):
            callback = getattr(self, self.callback)

            action_thread = threading.Thread(target=callback)
            action_thread.start()
            ThreadProgress(action_thread, _('processing'), _('done'))

    def initProject(self):
        """Initializes

        Initializes the PlatformIO project with selected environment
        """
        # check if it was already initialized (stop execution if it was)
        if(os.path.isfile(self.ini_path)):
            with open(self.ini_path) as file:
                if(self.environment in file.read()):
                    return

        # Run Command
        command = ['init', '-b %s' % (self.environment)]
        self.Commands.runCommand(command, "init_project_{0}")

        if(not self.Commands.error_running):
            if(self.is_native):
                return
                self.window.run_command('close_file')
                new_path = os.path.join(self.project_dir,
                                        'src',
                                        self.file_name)
                move(self.file_path, new_path)
                self.window.open_file(new_path)
                Preferences().set('init_queue', '')
            if(not self.is_native):
                self.overrideSrc()

    def build(self):
        """build

        Build the file in the current view using PlatformIO CLI. It first
        checks if the current environment was previously initialized
        """
        if(not self.is_iot):
            return

        self.message_queue = MessageQueue(self.console)
        self.message_queue.startPrint()
        self.message_queue.put(
            '[ Deviot {0} ] {1}\\n', version, self.file_name)

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
        """Upload

        Upload the current file to the select hardware, it checks if any
        programmer option was previously selected
        """
        if(not self.is_iot):
            return

        # check ota only for Espressif
        mdns = self.mDNSCheck()
        if(not mdns):
            return

        # Stop serial monitor
        Tools.closeSerialMonitors()

        self.message_queue = MessageQueue(self.console)
        self.message_queue.startPrint()
        self.message_queue.put('[ Deviot {0} ] {1}\\n', version, self.file_name)

        # initialize the sketch
        self.initProject()

        # add ota auth
        if(not self.auth):
            Preferences().set('auth', '0')
        self.authOTA()

        # check programmer
        programmer = Preferences().get("programmer", False)
        if("teensy" in self.environment):
            command = ['run', '-t', 'upload', '-e', '%s' % (self.environment)]
        elif(not programmer):
            command = ['run', '-t', 'upload', '--upload-port %s -e %s' %
                       (self.port, self.environment)]
        else:
            command = ['run', '-t', 'program', '-e', '%s' % (self.environment)]
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
        """Clean

        Remove the cached compiled files for the chosen environment
        """
        if(not self.is_iot):
            return

        command = ['run', '-t', 'clean', '-e', '%s' % (self.environment)]
        self.Commands.runCommand(command, "clean_built_files__{0}")

    def selectPort(self):
        """Port

        Shows the quick panel with the list of all ports currently available

        """

        from .JSONFile import JSONFile
        quick_path = Paths.getTemplateMenuPath('serial.json', user_path=True)
        serial = JSONFile(quick_path)

        quickPanel(serial.data, self.savePortCallback, index=self.sel_index)

    def saveBoardCallback(self, selected):
        """Chosen Board

        Callback to save the chosen option by the user in the preferences file

        Arguments:
            selected {[int]} -- index with the choosen option
        """
        if(selected != -1):
            choose = Menu().createBoardsMenu()
            board_id = choose[selected][1].split(' | ')[1]
            Preferences().boardSelected(board_id)
            Tools.saveEnvironment(board_id)
            Tools.userPreferencesStatus()
            self.beforeProcess(self.callback)

    def saveEnvironmetCallback(self, selected):
        """Chosen Environment

        Callback to save the chosen option by the user in the preferences file

        Arguments:
            selected {[int]} -- index with the choosen option
        """
        if(selected != -1):
            list = Menu().getEnvironments()
            env = list[0][selected][1].split(' | ')[1]
            Tools.saveEnvironment(env)
            Tools.userPreferencesStatus()
            self.environment = env
            self.beforeProcess(self.callback)

    def savePortCallback(self, selected):
        """Chosen Port

        Callback to save the chosen option by the user in the preferences file

        Arguments:
            selected {[int]} -- index with the choosen option
        """
        if(selected > 0):
            if(selected == 1):
                self.window.run_command('add_serial_ip')
            from .JSONFile import JSONFile
            quick_path = Paths.getTemplateMenuPath(
                'serial.json', user_path=True)
            serial = JSONFile(quick_path)
            self.ports_list = serial.data
            choose = self.ports_list
            id_port = choose[selected][0]
            if("COM" not in id_port):
                id_port = id_port
            self.port = id_port
            Preferences().set('id_port', id_port)
            Tools.userPreferencesStatus()

            if(self.callback == 'upload'):
                callback = getattr(self, self.callback)
                self.beforeProcess(callback)

    def overrideSrc(self):
        """
        Append in the platformio.ini file, the src_dir option
        to override the source folder where the sketch is stored
        (when the file haven't PlatformIO structure)

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
        """Programmer

        Adds the programmer strings in the platformio.ini file, it considerate
        environment and programmer selected

        Arguments:
            programmer {[str]} -- id of chosen option
        """
        # list of programmers
        if(programmer == "avr"):  # AVR ISP
            programmer_string = \
                "upload_protocol = stk500v1\n" \
                "upload_flags = -P$UPLOAD_PORT\n" \
                "upload_port = %s\r\n" % (self.port)
        elif(programmer == "avrmkii"):  # AVRISP mkII
            programmer_string = \
                "upload_protocol = stk500v2\n"\
                "upload_flags = -Pusb\r\n"
        elif(programmer == "usbtyni"):  # USBtinyISP
            programmer_string = "upload_protocol = usbtiny\r\n"
        elif(programmer == "arduinoisp"):  # ArduinoISP
            programmer_string = "upload_protocol = arduinoisp\r\n"
        elif(programmer == "usbasp"):  # USBasp
            programmer_string = "upload_protocol = usbasp\n" \
                "upload_flags = -Pusb\r\n"
        elif(programmer == "parallel"):  # Parallel Programmer
            programmer_string = "upload_protocol = dapa\n" \
                "upload_flags = -F\r\n"
        elif(programmer == "arduinoasisp"):  # Arduino as ISP
            programmer_string = "upload_protocol = stk500v1\n" \
                "upload_flags = -P$UPLOAD_PORT -b$UPLOAD_SPEED\n" \
                "upload_speed = 19200\n" \
                "upload_port = %s\r\n" % (self.port)
        else:
            programmer_string = False

        with open(self.ini_path, 'r') as file:
            if(programmer_string and programmer_string.split('\n')[0] in file.read()):
                return

        # Vars and Flags to process the file
        header_env = str.encode("[env:%s]" % self.environment)
        temp = os.path.join(self.project_dir, "temp")
        previous_prog = False
        writed = False
        found = False
        EOF = False

        # writing lines
        with open(self.ini_path, 'rb') as file, open(temp, 'wb') as new_file:
            while(True):
                line = file.readline()
                # End of File
                if(not line):
                    EOF = True
                # Search ENV
                if(header_env in line):
                    found = True
                # If previous programmer
                if(found and b'upload_protocol' in line and not previous_prog):
                    previous_prog = True
                # Not more previous programmer
                if(previous_prog and line == b'\r\n'):
                    previous_prog = -1
                # ENV Found
                if(found and line == b'\r\n' or previous_prog == -1 or EOF):
                    if(not writed and programmer_string):
                        new_file.write(str.encode(programmer_string))
                        writed = True
                # Write in the new file
                if(not previous_prog or previous_prog == -1):
                    new_file.write(line)
                # Stop Loop
                if(EOF):
                    break

        # rename temp file
        if(sublime.platform() == 'windows'):
            os.remove(self.ini_path)  # For windows only
        os.rename(temp, self.ini_path)  # Rename the new file

    def getMCU(self):
        """MCU

        Give the MCU for the current board selected
        Returns:
            [str] -- MCU type/name
        """
        # get data from user preference file
        is_native = Preferences().get('native')
        type_env = "env_selected" if not is_native else "native_env_selected"
        environment = Preferences().get(type_env, False)
        env_data = Menu().getTemplateMenu(file_name='platformio_boards.json',
                                          user_path=True)
        env_data = json.loads(env_data)
        selected = env_data[environment]['build']['mcu']
        return selected

    def authOTA(self):
        """OTA Authentication

        Adds OTA authentication (password) in the platformio.ini file
        based in the current environment chosen

        Arguments:
            password {[str]} -- password
        """
        password = Preferences().get('auth')
        header_env = str.encode("[env:%s]" % self.environment)
        auth_string = "upload_flags = --auth=%s\r\n" % password
        temp = os.path.join(self.project_dir, "temp")
        previous_auth = False
        writed = False
        found = False
        EOF = False

        # writing lines
        with open(self.ini_path, 'rb') as file, open(temp, 'wb') as new_file:
            while(True):
                line = file.readline()
                # End of File
                if(not line):
                    EOF = True
                # Search ENV
                if(header_env in line):
                    found = True
                # If previous auth
                if(found and b'--auth=' in line and not previous_auth):
                    previous_auth = True
                # Not more previous auth
                if(previous_auth and line == b'\r\n'):
                    previous_auth = -1
                # ENV Found
                if(found and line == b'\r\n' or previous_auth == -1 or EOF):
                    if(not writed and password != '0'):
                        new_file.write(str.encode(auth_string))
                        writed = True
                # Write in the new file
                if(not previous_auth or previous_auth == -1):
                    new_file.write(line)
                # Stop Loop
                if(EOF):
                    break

        # rename temp file
        if(sublime.platform() == 'windows'):
            os.remove(self.ini_path)  # For windows only
        os.rename(temp, self.ini_path)  # Rename the new file

    def mDNSCheck(self, feedback=True):
        """mDNS Available

        When a mDNS service is selected, allows to upload only espressif
        platforms, it's the only type of platform available to to OTA upload

        Returns:
            bool -- True if is possible to upload, False if isn't
        """
        is_native = Preferences().get('native')
        type_env = "env_selected" if not is_native else "native_env_selected"
        environment = Preferences().get(type_env, False)
        port = Preferences().get('id_port', False)

        if(not environment or not port):
            return False

        mcu = self.getMCU()

        if(port and "COM" not in port and "esp" not in mcu):
            if(feedback):
                sublime.message_dialog(_("ota_error_platform"))
            return False
        return True

    def saveAuthPassword(self, password):
        """Password

        Saves the password in the preferences file to OTA uploads

        Arguments:
            password {[str]} -- password
        """
        Preferences().set('auth', password)
        self.openInThread('upload')

    def openInThread(self, func, join=False):
        """Thread

        Function to open function/methods like build/upload/clean/ports and
        others in a new thread.


        Arguments:
            func {[str/obj]} -- If It's string, it calls beforeProcess first.
                                when isn't call the object directly

        Keyword Arguments:
            join {bool} -- use thread.join when it's True (default: {False})
        """
        if(type(func) is str):
            thread = threading.Thread(target=self.beforeProcess, args=(func,))
            thread.start()
        else:
            thread = threading.Thread(target=func)
            thread.start()
            if(join):
                thread.join()
        ThreadProgress(thread, _('processing'), _('done'))

    def saveCodeInFile(self, view):
        """
        If the sketch in the current view has been not saved, it generate
        a random name and stores in a temp folder.

        Arguments: view {ST Object} -- Object with multiples options of ST
        """
        ext = '.ino'

        tmp_path = Paths.getTempPath()
        file_name = str(time.time()).split('.')[0]
        self.file_path = os.path.join(tmp_path, file_name)
        self.file_path = os.path.join(self.file_path, 'src')
        os.makedirs(self.file_path)

        full_path = file_name + ext
        full_path = os.path.join(self.file_path, full_path)

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
        """
        Get the list of port currently available from PlatformIO CLI
        Returns:
            [list] -- all ports available
        """
        from . import Serial

        lista = [[_('select_port_list'), ""], [_('menu_add_ip'), ""]]

        index = 1
        current_port = Preferences().get('id_port', False)

        # serial ports
        serial = Serial.listSerialPorts()
        if(serial):
            for port in serial:
                index += 1
                lista.append([port, ""])
                if(current_port and current_port == port):
                    self.sel_index = index

        # mdns services
        mdns = Serial.listMdnsServices()
        if(mdns):
            for service in mdns:
                index += 1
                try:
                    service = json.loads(service)
                    one = service["server"][:-1]
                    two = service["properties"]["board"]
                    if(current_port and current_port == one):
                        self.sel_index = index

                    lista.append([one, two])
                except:
                    pass
        if(len(lista) == 2):
            lista = [[_('menu_none_serial_mdns'), ""], [_('menu_add_ip'), ""]]

        # save ports
        from .JSONFile import JSONFile
        quick_path = Paths.getTemplateMenuPath('serial.json', user_path=True)
        serial = JSONFile(quick_path)
        serial.setData(lista)
        serial.saveData()

        self.ports_list = lista
        self.selectPort()

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
    """Generate Files

    It calls the functions and methods to create the main menu, completions
    and syntax file
    """
    # create main files
    Menu().createMainMenu()
    Tools.createCompletions()
    Tools.createSyntaxFile()

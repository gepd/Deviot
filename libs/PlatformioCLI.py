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
from .configobj.configobj import ConfigObj

_ = I18n().translate


C = {
    'IOT': None,
    'SKETCHPATH': None,
    'SKETCHDIR': None,
    'SKETCHSIZE': None,
    'FILENAME': None,
    'NATIVE': None,
    'INIPATH': None,
    'ENVIRONMENT': None,
    'WORKINGPATH': None,
    'PORTSLIST': None,
    'PORT': None,
    'CALLBACK': None,
    'CMDS': None,
    'AUTH': None,
    'BUILD': True,
    'PORTINDEX': 0
}


class PlatformioCLI(CommandsPy):
    '''
    This class handle all the request to the platformio ecosystem.
    From the list of boards to the build/upload of the sketchs.
    More info about platformio in: http://platformio.org/

    Extends: CommandsPy
    '''

    def __init__(self):
        self.window = sublime.active_window()
        self.view = self.window.active_view()

    def checkIOT(self):
        C['SKETCHPATH'] = self.view.file_name()
        C['SKETCHSIZE'] = self.view.size()
        C['FILENAME'] = Tools.getNameFromPath(C['SKETCHPATH'])
        C['IOT'] = Tools.isIOTFile(C['SKETCHPATH'])

    def fileCheck(self, next):
        """
        Checks if the file can be processed, if it can't, shows an error
        in the console
        """

        # Get the initial info
        self.checkIOT()

        VIEWNAME = self.view.name().lower()
        CURRENTTIME = time.strftime('%H:%M:%S')
        message_error = None
        C['BUILD'] = True

        # avoid to do anything with a monitor view
        if(not C['SKETCHPATH'] and 'monitor' in VIEWNAME):
            message_error = 'invalid_file_{0}'

        # unsaved changes
        if (self.view.is_dirty()):
            self.view.run_command('save')

        # Empty sketch
        if(not C['SKETCHSIZE']):
            message_error = 'not_empty_sketch_{0}'

        # check if file is iot
        if(not C['IOT'] and C['SKETCHPATH']):
            message_error = 'not_iot_{0}{1}'

        # show error in console
        if(message_error):
            console = Console(self.window)
            self.message_queue = MessageQueue(console)
            self.message_queue.startPrint()
            self.message_queue.put('_deviot_{0}', version)
            self.message_queue.put(message_error, CURRENTTIME, C['FILENAME'])
            C['BUILD'] = False

        # continue if there is not error
        if(C['BUILD']):
            # store the callback
            C['CALLBACK'] = next

            # get the type of proyect
            self.projectRecognition()

    def projectRecognition(self):
        """
        Recognises if the current sketch is native or not
        """
        # save file not empty
        if(not C['SKETCHPATH']):
            self.saveCodeInFile()
            self.checkIOT()

        # type of project
        C['NATIVE'] = Tools.isNativeProject(self.view)

        # load paths
        C['WORKINGPATH'] = Tools.getWorkingPath(self.view)
        C['SKETCHDIR'] = Paths.getCWD(C['SKETCHPATH'])
        C['INIPATH'] = Tools.getInitPath(self.view)

        # force native
        if(Preferences().get('force_native', False)):
            if(not os.path.exists(C['INIPATH']) and
                    not C['SKETCHDIR'].endswith('src')):
                self.window.run_command('close_file')

                NEWPATH = os.path.join(C['WORKINGPATH'], 'src')
                Paths.makeFolder(NEWPATH)
                move(C['SKETCHPATH'], NEWPATH)
                C['SKETCHPATH'] = os.path.join(NEWPATH, C['FILENAME'])

                self.window.open_file(C['SKETCHPATH'])

        # check the requirements before process
        self.beforeProcess()

    def beforeProcess(self):
        """
        Check if all the requirements are met based in the type of command. If
        it's necessary shows the quick panel to choose an option
        """

        # if none board is selected show a quick panel list
        if(not Tools.checkEnvironments()):
            choose = Menu().createBoardsMenu()
            quickPanel(choose, self.saveBoardCallback)
            return

        # get the selected port
        C['PORT'] = Preferences().get('id_port', '')
        PORT = C['PORT']

        # check if the port is available
        if(C['CALLBACK'] == 'upload'):
            if(not C['PORTSLIST']):
                self.listSerialPorts()

            if(not any(PORT in x[0] for x in C['PORTSLIST']) or PORT == ''):
                self.openInThread(self.selectPort)
                return

            # check auth in esp
            MCU = self.getMCU()
            if("esp" in MCU and "COM" not in PORT and "tty" not in PORT):
                from . import Serial
                saved_auth = Preferences().get('auth', '0')
                mdns = Serial.listMdnsServices()

                for service in mdns:
                    try:
                        service = json.loads(service)
                        ip = service['ip']
                        if(ip == PORT):
                            auth = service["properties"]["auth_upload"]
                            C['AUTH'] = True if auth == 'yes' else False
                    except:
                        pass

                # check if auth is required
                if(C['AUTH']):
                    if(saved_auth == '0' and self.mDNSCheck()):
                        self.window.show_input_panel(
                            _("pass_caption"), '', self.saveAuthPass, None, None)
                        return
                else:
                    Preferences().set('auth', '0')

        # Create and store the console
        WORKINGPATH = C['WORKINGPATH']
        C['CONSOLE'] = Console(self.window)
        C['CMDS'] = CommandsPy(console=C['CONSOLE'], cwd=WORKINGPATH)
        Paths.makeFolder(WORKINGPATH)

        # Get the current environment
        C['ENVIRONMENT'] = Tools.getEnvironment()

        # avoid an error in a non native project if the folder of the
        # sketch has been renamed
        if(not C['NATIVE'] and os.path.exists(C['INIPATH'])):
            INIFILE = ConfigObj(C['INIPATH'])

            # check src_dir
            if('src_dir' in INIFILE['platformio']):
                if(INIFILE['platformio']['src_dir'] is not C['SKETCHDIR']):
                    INIFILE['platformio']['src_dir'] = C['SKETCHDIR']
                    INIFILE.write()

        # Call method in a new thread
        callback = getattr(self, C['CALLBACK'])
        self.openInThread(callback)

    def initProject(self):
        """
        Initializes the PlatformIO project with selected environment
        """

        # check if it was already initialized (stop execution if it was)
        CMD = C['CMDS']
        NATIVE = C['NATIVE']
        ENVIRONMENT = C['ENVIRONMENT']
        INIFILE = ConfigObj(C['INIPATH'])

        # checks if the environment was previously initialized
        for env in INIFILE:
            if(ENVIRONMENT in env):
                return None

        # Run Command
        command = ['init', '-b %s' % (ENVIRONMENT)]
        CMD.runCommand(command, "init_project_{0}")

        # structure the project as native or not native
        if(not CMD.error_running):
            if(not NATIVE):
                self.overrideSrc()

    def build(self):
        """
        Build the file in the current view using PlatformIO CLI. It first
        checks if the current environment was previously initialized
        """

        CMD = C['CMDS']
        self.message_queue = MessageQueue(C['CONSOLE'])
        self.message_queue.startPrint()
        self.message_queue.put('[ Deviot {0} ] {1}\\n', version, C['FILENAME'])

        # initialize the sketch
        self.initProject()

        # add the programmer option to the platformio.ini
        programmer = Preferences().get("programmer", False)
        self.programmer(programmer)

        # stop if there is an error
        if(CMD.error_running):
            return

        command = ['run', '-e %s' % C['ENVIRONMENT']]
        CMD.runCommand(command, "built_project_{0}")

        if(CMD.error_running):
            exec_view = self.window.find_output_panel('exec')
            Tools.ERRORS_LIST.extend(Tools.highlightError(exec_view))

    def upload(self):
        """
        Upload the current file to the select hardware, it checks if any
        programmer option was previously selected
        """
        if(not C['IOT']):
            return

        CMD = C['CMDS']
        PORT = C['PORT']
        ENVIRONMENT = C['ENVIRONMENT']

        # check ota only for Espressif
        mdns = self.mDNSCheck()
        if(not mdns):
            return

        # Stop serial monitor
        Tools.closeSerialMonitors()

        self.message_queue = MessageQueue(C['CONSOLE'])
        self.message_queue.startPrint()
        self.message_queue.put('[ Deviot {0} ] {1}\\n', version, C['FILENAME'])

        # initialize the sketch
        self.initProject()

        # get programmer preference
        programmer = Preferences().get("programmer", False)

        # Create command
        if("teensy" in ENVIRONMENT):
            command = ['run', '-t', 'upload', '-e', '%s' % (ENVIRONMENT)]
        elif(not programmer):
            command = ['run', '-t', 'upload', '--upload-port %s -e %s' %
                       (PORT, ENVIRONMENT)]
        else:
            command = ['run', '-t', 'program', '-e', '%s' % (ENVIRONMENT)]

        # add the programmer option
        self.programmer(programmer)

        # add ota auth
        self.authOTA()

        # run command
        CMD.runCommand(command, "uploading_firmware_{0}")

        # start the monitor serial if was running previously
        if(not CMD.error_running):
            autorun = Preferences().get('autorun_monitor', False)
            if(autorun):
                Tools.toggleSerialMonitor()
                Preferences().set('autorun_monitor', False)
        else:
            exec_view = self.window.find_output_panel('exec')
            Tools.ERRORS_LIST.extend(Tools.highlightError(exec_view))
        self.message_queue.stopPrint()

    def clean(self):
        """
        Remove the cached compiled files for the chosen environment
        """
        if(not C['IOT']):
            return

        CMD = C['CMDS']

        command = ['run', '-t', 'clean', '-e', '%s' % (C['ENVIRONMENT'])]
        CMD.runCommand(command, "clean_built_files__{0}")

    def selectPort(self):
        """
        Shows the quick panel with the list of all ports currently available

        """

        # call the list of ports only if wasn't called previously
        if(not C['PORTSLIST']):
            self.listSerialPorts()

        # show quick panel
        quickPanel(C['PORTSLIST'], self.savePortCallback, index=C['PORTINDEX'])

    def saveBoardCallback(self, selected):
        """
        Callback to save the chosen option by the user in the preferences file

        Arguments:
            selected {int} -- index with the choosen option
        """
        if(selected != -1):
            choose = Menu().createBoardsMenu()
            board_id = choose[selected][1].split(' | ')[1]

            # store data
            Preferences().boardSelected(board_id)
            Tools.saveEnvironment(board_id)
            Tools.userPreferencesStatus()

            # callback
            self.beforeProcess()

    def savePortCallback(self, selected):
        """
        Callback to save the chosen option by the user in the preferences file

        Arguments:
            selected {int} -- index with the choosen option
        """
        if(selected > 0):
            # if option was add serial port
            if(selected == 1):
                self.window.run_command('add_serial_ip')
                return

            # read option selected and stored it
            try:
                port_bar = C['PORTSLIST'][selected][0].split(' ')[0]
                id_port = C['PORTSLIST'][selected][0].split(' ')[2]
            except:
                id_port = C['PORTSLIST'][selected][0]
                port_bar = C['PORTSLIST'][selected][0]

            Preferences().set('id_port', id_port)
            Preferences().set('port_bar', port_bar)

            Tools.userPreferencesStatus()

            C['PORT'] = id_port

            # callback
            if(C['CALLBACK'] == 'upload'):
                callback = getattr(self, C['CALLBACK'])
                self.beforeProcess()

            if(C['CALLBACK'] == 'monitor'):
                self.window.run_command('serial_monitor_run')

    def overrideSrc(self):
        """
        Append in the platformio.ini file, the src_dir option
        to override the source folder where the sketch is stored
        (when the file haven't PlatformIO structure)
        """
        # open platformio.ini
        INIFILE = ConfigObj(C['INIPATH'])

        # set 'src_dir' in [platformio]
        source = {'src_dir': C['SKETCHDIR']}
        INIFILE['platformio'] = source

        # write in file
        INIFILE.write()

    def programmer(self, programmer):
        """
        Adds the programmer strings in the platformio.ini file, it considerate
        environment and programmer selected

        Arguments:
            programmer {str} -- id of chosen option
        """

        # list of programmers
        flags = {
            'avr':          {"upload_protocol": "stk500v1",
                             "upload_flags": "-P$UPLOAD_PORT",
                             "upload_port": C['PORT']},
            'avrmkii':      {"upload_protocol": "stk500v2",
                             "upload_flags": "-Pusb"},
            'usbtyni':      {"upload_protocol": "usbtiny"},
            'arduinoisp':   {"upload_protocol": "arduinoisp"},
            'usbasp':       {"upload_protocol": "usbasp",
                             "upload_flags": "-Pusb"},
            'parallel':     {"upload_protocol": "dapa",
                             "upload_flags": "-F"},
            'arduinoasisp': {"upload_protocol": "stk500v1",
                             "upload_flags": "-P$UPLOAD_PORT -b$UPLOAD_SPEED",
                             "upload_speed": "19200",
                             "upload_port": C['PORT']}
        }

        # prevent to do anything if none environment is selected
        if(not C['ENVIRONMENT']):
            return

        # open platformio.ini and get the environment
        INIFILE = ConfigObj(C['INIPATH'])
        ENVIRONMENT = 'env:%s' % C['ENVIRONMENT']

        # stop if environment wasn't initialized yet
        if(ENVIRONMENT not in INIFILE):
            return

        ENV = INIFILE[ENVIRONMENT]
        rm = ['upload_protocol', 'upload_flags', 'upload_speed', 'upload_port']

        # remove previous configuration
        for line in rm:
            if(line in ENV):
                ENV.pop(line)

        # add programmer option if it was selected
        if(programmer):
            ENV.merge(flags[programmer])

        # save in file
        INIFILE.write()

    def getMCU(self):
        """
        Give the MCU for the current board selected
        Returns:
            [str] -- MCU type/name
        """

        # get data from user preference file
        boardsfile = 'platformio_boards.json'
        environment = Tools.getEnvironment()
        env_data = Menu().getTemplateMenu(file_name=boardsfile, user_path=True)
        env_data = json.loads(env_data)

        try:
            selected = env_data[environment]['build']['mcu']
        except:  # PlatformIO 3
            for env in env_data:
                if(env['id'] == environment):
                    selected = env['mcu']
                    break

        return selected

    def authOTA(self):
        """
        Adds OTA authentication (password) in the platformio.ini file
        based in the current environment chosen

        Arguments:
            password {str} -- password
        """
        password = Preferences().get('auth', '0')
        INIFILE = ConfigObj(C['INIPATH'])
        ENVIRONMENT = 'env:%s' % C['ENVIRONMENT']

        # remove flag
        if(not password or password == '0'):
            if('upload_flags' in INIFILE[ENVIRONMENT]):
                INIFILE[ENVIRONMENT].pop('upload_flags')
                INIFILE.write()
            return

        # Write flag
        FLAG = {'upload_flags': '--auth=%s' % password}
        INIFILE[ENVIRONMENT].merge(FLAG)
        INIFILE.write()

    def mDNSCheck(self, feedback=True):
        """
        When a mDNS service is selected, allows to upload only espressif
        platforms, it's the only type of platform available to to OTA upload

        Returns:
            bool -- True if is possible to upload, False if isn't
        """
        from re import search

        PORT = Preferences().get('id_port', False)
        environment = Tools.getEnvironment()

        # stop if none environment or port was previously selected
        if(not environment or not PORT):
            return False

        MCU = self.getMCU()

        if(search(r"[\d{3}\.]{3}", PORT) is not None and
                "esp" not in MCU.lower()):
            if(feedback):
                self.message_queue = MessageQueue(C['CONSOLE'])
                self.message_queue.startPrint()
                self.message_queue.put('[ Deviot {0} ] {1}\\n',
                                       version,
                                       C['FILENAME'])
                self.message_queue.put('ota_error_platform')
            return False
        return True

    def saveAuthPass(self, password):
        """
        Saves the password in the preferences file to OTA uploads

        Arguments:
            password {str} -- password
        """
        Preferences().set('auth', password)
        self.openInThread('upload')

    def monitorCall(self):
        """
        Make to select a serial port when run a monitor serial and
        none port was selected
        """
        C['CALLBACK'] = 'monitor'
        self.openInThread(self.selectPort)

    def openInThread(self, func, join=False):
        """
        Function to open function/methods like build/upload/clean/ports and
        others in a new thread.

        Arguments:
            func {str/obj} -- If It's string, it calls beforeProcess first.
                                when isn't call the object directly
            join {bool} -- use thread.join when it's True (default: {False})
        """
        if(type(func) is str):
            thread = threading.Thread(target=self.fileCheck, args=(func,))
            thread.start()
        else:
            thread = threading.Thread(target=func)
            thread.start()
            if(join):
                thread.join()
        ThreadProgress(thread, _('processing'), _('done'))

    def saveCodeInFile(self):
        """
        If the sketch in the current view has been not saved, it generate
        a random name and stores in a temp folder.

        Arguments: view {ST Object} -- Object with multiples options of ST
        """
        ext = '.ino'

        tmppath = Paths.getTempPath()
        filename = str(time.time()).split('.')[0]
        filepath = os.path.join(tmppath, filename, 'src')

        Paths.makeFolder(filepath)

        fullpath = filename + ext
        fullpath = os.path.join(filepath, fullpath)

        region = sublime.Region(0, self.view.size())
        text = self.view.substr(region)
        file = JSONFile(fullpath)
        file.writeFile(text)

        self.view.set_scratch(True)
        window = sublime.active_window()
        window.run_command('close')
        self.view = window.open_file(fullpath)

    def listSerialPorts(self):
        """
        Get the list of port currently available from PlatformIO CLI
        Returns:
            [list] -- all ports available
        """
        from . import Serial

        lista = [[_('select_port_list').upper(), ""], [_('menu_add_ip'), ""]]
        current_port = Preferences().get('id_port', False)
        index = 1

        # serial ports
        serial = Serial.listSerialPorts()
        if(serial):
            for port in serial:
                index += 1
                lista.append([port, ""])
                if(current_port and current_port == port):
                    C['PORTINDEX'] = index

        # mdns services
        mdns = Serial.listMdnsServices()

        if(mdns):
            for service in mdns:
                index += 1
                try:
                    service = json.loads(service)
                    one = service["server"][:-1] + ' | ' + service["ip"]
                    two = service["properties"]["board"]
                    if(current_port and current_port == service["ip"]):
                        C['PORTINDEX'] = index
                    lista.append([one, two])
                except:
                    pass

        # none port found
        if(len(lista) == 2):
            lista = [[_('menu_none_serial_mdns'), ""], [_('menu_add_ip'), ""]]

        # store ports list
        C['PORTSLIST'] = lista

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
    """
    It calls the functions and methods to create the main menu, completions
    and syntax file
    """

    Menu().createMainMenu()
    Tools.createCompletions()
    Tools.createSyntaxFile()

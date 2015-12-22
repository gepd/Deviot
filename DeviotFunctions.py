#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import os
import re
import time
import sublime
import codecs
import json

if(int(sublime.version()) < 3000):
    import DeviotCommands
    import DeviotPaths
    import DeviotSerial
else:
    from . import DeviotCommands
    from . import DeviotPaths
    from . import DeviotSerial


class JSONFile(object):
    '''Handle JSON Files

    This class allow to load and save JSON files
    '''

    def __init__(self, path):
        '''JSONFile Construct

        This construct load a file when is called and
        load the information in a global variable

        Arguments:
                path {string} -- Full path of the JSON file
        '''
        super(JSONFile, self).__init__()
        self.setEncoding()
        self.data = {}
        self.path = path
        self.loadData()

    def loadData(self):
        '''Load JSON File

        Load the content of a JSON file and
        deserialize it to set the information
        in a global object called data
        '''
        try:
            text = self.readFile()
        except:
            return

        try:
            self.data = json.loads(text)
        except:
            pass

    def getData(self):
        '''Ouput data

        It's an alternative way to get the data obtained from
        the JSON file. The other way is using only the 'data'
        global object.

        Returns:
                {miltiple} -- mutiple type of data stored in the
                                          differents files.
        '''
        return self.data

    def setData(self, data):
        '''Set the JSON data

        Save the data in the file setted on the
        construct. This method is most used in
        the preferences class.

        Arguments:
                data {string} -- data to save in the JSON file.
        '''
        self.data = data
        self.saveData()

    def saveData(self):
        '''Save JSON data

        Serialize the data stored in the global object data
        and call to Write file. This function is called automatically
        when any data is set in the method SetData.

        '''
        text = json.dumps(self.data, sort_keys=True, indent=4)
        self.writeFile(text)

    def readFile(self):
        '''Read File

        Read the data from the file specified in the global object path.
        The data readed is encoded with the format specified in the global
        object encoding, by default this object is UTF-8. Use this method
        if you don't want to modify the data received from the file.

        Returns:
                text {string} -- encoded text readed from file
        '''
        text = ''

        try:
            with codecs.open(self.path, 'r', self.encoding) as file:
                text = file.read()
        except (IOError, UnicodeError):
            pass

        return text

    def writeFile(self, text, append=False):
        '''Write File

        Write the data passed in a file specified in the global object path.
        This method is called automatically by saveData, and encode the text
        in the format specified in the global object encoding, by default this
        object is UTF-8. Use this method if you don't want to modify the data
        to write.

        Arguments:
                text {string} -- Text to write in the file

        Keyword Arguments:
                append {boolean} -- Set to True if you want to append the data
                in the file (default: False)
        '''
        mode = 'w'

        if append:
            mode = 'a'
        try:
            with codecs.open(self.path, mode, self.encoding) as file:
                file.write(text)
        except (IOError, UnicodeError):
            pass

    def setEncoding(self, encoding='utf-8'):
        '''Change encoding

        Call this method to change the format to encode the files when you
        load it or save it.

        Keyword Arguments:
                encoding {string} -- Format to encoding (default: UTF-8 )
        '''
        self.encoding = encoding


class Menu(object):
    '''Plugin Menu

    Class to handle the differents option in the plugin menu.
    '''

    def __init__(self):
        '''Construct

        Call the construct of the command library to make the
        differents call by CLI
        '''
        super(Menu, self).__init__()

    def saveAPIBoards(self):
        '''Save board list

        Save the JSON object in a specific JSON file
        '''
        boards = PlatformioCLI().getAPIBoards()

        self.saveTemplateMenu(
            data=boards, file_name='platformio_boards.json', user_path=True)
        self.saveEnvironmentFile()

    def createBoardsMenu(self):
        '''Board menu

        Load the JSON file with the list of all boards and re order it
        based on the vendor. after that format the data to operate with
        the standards required for the ST

        Returns:
                {json array} -- list of all boards to show in the menu
        '''
        vendors = {}
        boards = []

        platformio_data = self.getTemplateMenu(
            file_name='platformio_boards.json', user_path=True)

        if(not platformio_data):
            return

        platformio_data = json.loads(platformio_data)

        # searching data
        for datakey, datavalue in platformio_data.items():
            for infokey, infovalue in datavalue.items():
                vendor = datavalue['vendor']
                if('name' in infokey):
                    temp_info = {}
                    temp_info['caption'] = infovalue
                    temp_info['command'] = 'select_board'
                    temp_info['checkbox'] = True
                    temp_info['args'] = {'board_id': datakey}
                    children = vendors.setdefault(vendor, [])
                    children.append(temp_info)

        # reorganizing data
        for vendor, children in vendors.items():
            children = sorted(children, key=lambda x: x['caption'])
            boards.append({'caption': vendor,
                           'children': children})

        boards = sorted(boards, key=lambda x: x['caption'])

        return boards

    def saveEnvironmentFile(self):
        '''Board menu

        Load the JSON file with the list of all boards and re order it
        based on the vendor. after that format the data to operate with
        the standards required for the ST

        Returns:
                {json array} -- list of all boards to show in the menu
        '''
        boards_list = []

        platformio_data = self.getTemplateMenu(
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
        self.saveTemplateMenu(boards_list, 'env_boards.json', user_path=True)

    def createEnvironmentMenu(self):
        # load
        env_selecs = Preferences().get('board_id', '')
        env_boards = self.getTemplateMenu('env_boards.json', user_path=True)

        if(not env_boards):
            return

        environments = []

        # search
        for board in env_boards:
            for selected in env_selecs:
                try:
                    environments.append(board[selected]['children'][0])
                except:
                    pass

        # save
        env_menu = self.getTemplateMenu(file_name='environment.json')
        env_menu[0]['children'][0]['children'] = environments
        self.saveSublimeMenu(data=env_menu,
                             sub_folder='environment',
                             user_path=True)

    def createSerialPortsMenu(self):
        '''Serial ports

        Create the list menu 'Serial ports' with the list of all the
        availables serial ports
        '''
        port_list = DeviotSerial.listSerialPorts()

        if not port_list:
            return False

        menu_preset = self.getTemplateMenu(file_name='serial.json')
        menu_ports = []

        for port in port_list:
            menu_ports.append({'caption': port,
                               'command': 'select_port',
                               'checkbox': True,
                               'args': {'id_port': port}})

        menu_preset[0]['children'][0]['children'] = menu_ports

        self.saveSublimeMenu(data=menu_preset,
                             sub_folder='serial',
                             user_path=True)

    def createMainMenu(self):
        '''Main menu

        Creates the main menu with the differents options
        including boards, libraries, COM ports, and user
        options.
        '''
        boards = self.createBoardsMenu()

        if(not boards):
            return False

        menu_data = self.getTemplateMenu(file_name='menu_main.json')

        for first_menu in menu_data[0]:
            for second_menu in menu_data[0][first_menu]:
                if 'children' in second_menu:
                    if(second_menu['id'] == 'initialize'):
                        second_menu['children'] = boards

        self.saveSublimeMenu(data=menu_data, user_path=True)

        env_path = DeviotPaths.getSublimeMenuPath(
            'environment', user_path=True)

        if(os.path.isfile(env_path)):
            self.createEnvironmentMenu()

    def getTemplateMenu(self, file_name, user_path=False):
        file_path = DeviotPaths.getTemplateMenuPath(file_name, user_path)
        preset_file = JSONFile(file_path)
        preset_data = preset_file.getData()
        return preset_data

    def saveTemplateMenu(self, data, file_name, user_path=False):
        file_path = DeviotPaths.getTemplateMenuPath(file_name, user_path)
        preset_file = JSONFile(file_path)
        preset_file.setData(data)
        preset_file.saveData()

    def getSublimeMenu(self, user_path=False):
        menu_path = DeviotPaths.getSublimeMenuPath(user_path)
        menu_file = JSONFile(menu_path)
        menu_data = menu_file.getData()
        return menu_data

    def saveSublimeMenu(self, data, sub_folder=False, user_path=False):
        menu_file_path = DeviotPaths.getSublimeMenuPath(sub_folder, user_path)
        file_menu = JSONFile(menu_file_path)
        file_menu.setData(data)
        file_menu.saveData()


class Preferences(JSONFile):
    '''Preferences

    Class to handle the preferences of the plugin

    Extends:
            JSONFile
    '''

    def __init__(self):
        '''Construct

        Path loads the file where the preferences are stored,
        Doing that you avoid to pass the path every time you
        need to get or set any preference.
        '''
        path = DeviotPaths.getPreferencesFile()
        super(Preferences, self).__init__(path)

    def set(self, key, value):
        '''Set value

        Save a value in the preferences file using a list and
        dictionaries.

        Arguments:
                key {string} -- identifier of the preference
                value {[type]} -- value of the preference
        '''
        self.data[key] = value
        self.saveData()

    def get(self, key, default_value=False):
        '''Get Value

        Get a value in the preferences file stored as a list and
        dictionaries format.

        Arguments:
                key {string} -- identifier of the preference

        Keyword Arguments:
                default_value {string} -- if there is none value stored
                you can set a default value (default: False)

        Returns:
                {string} -- Value of the preference
        '''
        value = self.data.get(key, default_value)
        return value

    def boardSelected(self, board_id):
        '''Choosed board

        Add or delete the board selected from the preferences
        files. The boards are formated in a dictionary in the
        the list 'board id'

        Arguments:
                board_id {string} -- identifier if the board selected
        '''
        file_data = self.get('board_id', '')

        if(file_data):
            if board_id in file_data:
                self.data.setdefault('board_id', []).remove(board_id)
                try:
                    self.set('env_selected', '')
                except:
                    pass
            else:
                self.data.setdefault('board_id', []).append(board_id)
            self.saveData()
        else:
            self.set('board_id', [board_id])
        Menu().createEnvironmentMenu()

    def checkBoard(self, board_id):
        '''Is checked

        Check if is necessary to mark or unmark the board selected

        Arguments:
                board_id {string} -- identifier of the board selected
        '''
        check = False
        if(self.data):
            check_boards = self.get('board_id', '')

            if board_id in check_boards:
                check = True
        return check


class PlatformioCLI(DeviotCommands.CommandsPy):
    '''Platformio

    This class handle all the request to the platformio ecosystem.
    From the list of boards to the build/upload of the sketchs.
    More info about platformio in: http://platformio.org/

    Extends:
            DeviotCommands.CommandsPy
    '''

    def __init__(self, view=False):
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
        checkFile = stateFile(view)

        if(not checkFile):
            print('This is not a IoT File')
            self.execute = False

        self.Preferences = Preferences()
        env_path = self.Preferences.get('CMD_ENV_PATH', False)
        self.Commands = DeviotCommands.CommandsPy(env_path)

        if(view):
            currentFilePath = DeviotPaths.getCurrentFilePath(view)
            cwd = DeviotPaths.getCWD(currentFilePath)
            parent = DeviotPaths.getParentCWD(currentFilePath)
            library = DeviotPaths.getLibraryPath()
            tmp_path = DeviotPaths.getDeviotTmpPath()
            init = False

            for file in os.listdir(parent):
                if(file.endswith('platformio.ini')):
                    self.working_dir = parent
                    init = True

            if(not init):
                self.working_dir = tmp_path
                os.environ['PLATFORMIO_SRC_DIR'] = cwd
                os.environ['PLATFORMIO_LIB_DIR'] = library

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

    def initSketchProject(self):
        '''CLI

        command to initialize the board(s) selected by the user. This
        function can only be use if the workig file is an IoT type
        (checked by isIOTFile)
        '''
        init_boards = self.getSelectedBoards()

        if(not init_boards):
            print('None board Selected')
            self.Commands.error_running = True
            return

        command = ['init', '%s' % (init_boards)]

        print('Initializing the project')
        self.Commands.runCommand(command, self.working_dir, verbose=True)

    def buildSketchProject(self):
        '''CLI

        Command to build the current working sketch, it must to be IoT
        type (checked by isIOTFile)
        '''
        if(not self.execute):
            return

        # initialize the sketch
        self.initSketchProject()

        if(not self.Commands.error_running):
            print('Building the project')

            command = ['run']

            self.Commands.runCommand(command, self.working_dir, verbose=True)

            if(not self.Commands.error_running):
                print('Success')
                self.Preferences.set('builded_sketch', True)
            else:
                print('Error')
                self.Preferences.set('builded_sketch', False)

    def uploadSketchProject(self):
        '''CLI

        Upload the sketch to the select board to the select COM port
        it returns an error if any com port is selected
        '''
        if(not self.execute):
            return

        builded_sketch = self.Preferences.get('builded_sketch', '')

        if(builded_sketch):
            id_port = self.Preferences.get('id_port', '')
            env_sel = self.Preferences.get('env_selected', '')

            if(not id_port or not env_sel):
                print('Not COM port or environment selected')
                return

            command = ['run', '-t uploadlazy --upload-port %s -e %s' %
                       (id_port, env_sel)]

            self.Commands.runCommand(command, self.working_dir, verbose=True)

            if(not self.Commands.error_running):
                print("Success")

    def cleanSketchProject(self):
        '''CLI

        Delete compiled object files, libraries and firmware/program binaries
        if a sketch has been built previously
        '''

        builded_sketch = self.Preferences.get('builded_sketch', '')

        if(builded_sketch):
            print('Cleaning')
            command = ['run', '-t clean']

            self.Commands.runCommand(command, self.working_dir, verbose=True)

            if(not self.Commands.error_running):
                self.Preferences.set('builded_sketch', False)
                print("Success")

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


def platformioCheck():
    '''Platformio
    Check if is possible to run a platformio command
    if can't check for the preferences file,

    '''
    command = ['--version']

    Run = DeviotCommands.CommandsPy()
    version = Run.runCommand(command, setReturn=True)
    version = re.sub(r'\D', '', version)

    # Check the minimum version
    if(not Run.error_running and int(version) < 260):
        Preferences().set('enable_menu', False)
        temp_menu = Menu().getSublimeMenu()

        temp_menu[0]['children'][0]['caption'] = 'Please upgrade Platformio'
        temp_menu[0]['children'][1] = 0

        Menu().saveSublimeMenu(temp_menu)
        return False

    # Check if the environment path is set in preferences file
    if(Run.error_running):
        Preferences().set('enable_menu', False)
        CMD_ENV_PATH = Preferences().get('CMD_ENV_PATH', False)

        if(not CMD_ENV_PATH):
            # Create prefences file
            Preferences().set('CMD_ENV_PATH', 'YOUR-ENVIRONMENT-PATH-HERE')
            return False

    Preferences().set('enable_menu', True)

    install_menu_path = DeviotPaths.getSublimeMenuPath()
    user_menu_path = DeviotPaths.getSublimeMenuPath(user_path=True)

    # Delete requirement/install file menu
    if(os.path.exists(install_menu_path)):
        os.remove(install_menu_path)

    # Creates new menu
    if(not os.path.exists(user_menu_path)):
        Menu().createMainMenu()

    # Run serial port listener
    Serial = DeviotSerial.SerialListener(func=Menu().createSerialPortsMenu)
    Serial.start()

    return True


def isIOTFile(view):
    '''IoT File

    Check if the file in the current view of ST is an allowed
    IoT file, the files are specified in the exts variable.

    Arguments:
            view {st object} -- stores many info related with ST
    '''
    exts = ['ino', 'pde', 'cpp', 'c', '.S']
    file_name = view.file_name()

    if file_name and file_name.split('.')[-1] in exts:
        return True
    return False


def setStatus(view):
    '''Status bar

    Set the info to show in the status bar of Sublime Text.
    This info is showing only when the working file is considered IoT

    Arguments:
            view {st object} -- stores many info related with ST
    '''
    info = []

    if isIOTFile(view):
        info.append('Deviot ' + getVersion())
        full_info = ' | '.join(info)

        view.set_status('Deviot', full_info)


def stateFile(view):
    if(not isIOTFile(view)):
        return False

    ext = '.ino'

    window = view.window()
    views = window.views()

    if view not in views:
        view = window.active_view()
    if view.file_name() is None:
        tmp_path = DeviotPaths.getDeviotTmpPath()
        file_name = str(time.time()).split('.')[1]
        file_path = os.path.join(tmp_path, file_name)
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

    if view.is_dirty():
        view.run_command('save')

    return True


def getVersion():
    '''Plugin Version

    Get the current version of the plugin stored in the preferences file.

    Returns:
            {String} -- Version of the file (only numbers)
    '''
    return Preferences().get('plugin_version')


def setVersion(version):
    '''Plugin Version

    Save the current version of the plugin in the preferences file.

    Returns:
            {String} -- Version of the file (only numbers)
     '''
    Preferences().set('plugin_version', version)

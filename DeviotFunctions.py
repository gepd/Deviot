#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import os
import sublime
import codecs
import json
import shutil


if(int(sublime.version()) < 3000):
    import DeviotCommands
    import DeviotPaths
else:
    from . import DeviotCommands
    from . import DeviotPaths


class JSONFile(object):
    """Handle JSON Files

    This class allow to load and save JSON files
    """

    def __init__(self, path):
        """JSONFile Construct

        This construct load a file when is called and
        load the information in a global variable

        Arguments:
                path {string} -- Full path of the JSON file
        """
        super(JSONFile, self).__init__()
        self.setEncoding()
        self.data = {}
        self.path = path
        self.loadData()

    def loadData(self):
        """Load JSON File

        Load the content of a JSON file and
        deserialize it to set the information
        in a global object called data
        """
        try:
            text = self.readFile()
        except:
            return

        try:
            self.data = json.loads(text)
        except:
            pass

    def getData(self):
        """Ouput data

        It's an alternative way to get the data obtained from
        the JSON file. The other way is using only the "data"
        global object.

        Returns:
                {miltiple} -- mutiple type of data stored in the
                                          differents files.
        """
        return self.data

    def setData(self, data):
        """Set the JSON data

        Save the data in the file setted on the
        construct. This method is most used in
        the preferences class.

        Arguments:
                data {string} -- data to save in the JSON file.
        """
        self.data = data
        self.saveData()

    def saveData(self):
        """Save JSON data

        Serialize the data stored in the global object data
        and call to Write file. This function is called automatically
        when any data is set in the method SetData.

        """
        text = json.dumps(self.data, sort_keys=True, indent=4)
        self.writeFile(text)

    def readFile(self):
        """Read File

        Read the data from the file specified in the global object path.
        The data readed is encoded with the format specified in the global
        object encoding, by default this object is UTF-8. Use this method
        if you don't want to modify the data received from the file.

        Returns:
                text {string} -- encoded text readed from file
        """
        text = ''

        try:
            with codecs.open(self.path, 'r', self.encoding) as file:
                text = file.read()
        except (IOError, UnicodeError):
            pass

        return text

    def writeFile(self, text, append=False):
        """Write File

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
        """
        mode = 'w'

        if append:
            mode = 'a'
        try:
            with codecs.open(self.path, mode, self.encoding) as file:
                file.write(text)
        except (IOError, UnicodeError):
            pass

    def setEncoding(self, encoding='utf-8'):
        """Change encoding

        Call this method to change the format to encode the files when you
        load it or save it.

        Keyword Arguments:
                encoding {string} -- Format to encoding (default: UTF-8 )
        """
        self.encoding = encoding


class Menu(object):
    """Plugin Menu

    Class to handle the differents option in the plugin menu.
    """

    def __init__(self):
        """Construct

        Call the construct of the command library to make the
        differents call by CLI
        """
        super(Menu, self).__init__()

    def saveAPIBoards(self):
        """Save board list

        Save the JSON object in a specific JSON file
        """
        boards = PlatformioCLI().getAPIBoards()

        file = JSONFile(DeviotPaths.getDeviotBoardsPath())
        file.setData(boards)
        file.saveData()

    def getFileBoards(self):
        """Get Board File

        Load the board list stored in a JSON file and
        return the data. This function is used to avoid
        always download the list from the web.

        Returns:
                {json object} -- list with all boards in a JSON format
        """
        file = JSONFile(DeviotPaths.getDeviotBoardsPath())
        boards = file.getData()
        return boards

    def createBoardsMenu(self):
        """Board menu

        Load the JSON file with the list of all boards and re order it
        based on the vendor. after that format the data to operate with
        the standards required for the ST

        Returns:
                {json array} -- list of all boards to show in the menu
        """
        vendors = {}
        boards = []

        datas = json.loads(self.getFileBoards())

        for datakey, datavalue in datas.items():
            for infokey, infovalue in datavalue.items():
                vendor = datavalue['vendor']
                if(infokey == 'name'):
                    name = infovalue.replace(vendor + " ", "", 1)
                    children = vendors.setdefault(vendor, [])
                    children.append({'caption': name,
                                     'command': 'select_board',
                                     'id': datakey,
                                     'checkbox': True,
                                     'args': {'board_id': datakey}})

        for vendor, children in vendors.items():
            boards.append({'caption': vendor,
                           'children': children})

        boards = sorted(boards, key=lambda x: x['caption'])

        return boards

    def createSerialPortsMenu(self):
        """Serial ports

        Create the list menu "Serial ports" with the list of all the
        availables serial ports
        """

        menu_path_preset = DeviotPaths.getDeviotMenuPath('serial')
        menu_preset = JSONFile(menu_path_preset)
        menu_preset = menu_preset.getData()

        port_list = PlatformioCLI().getAPICOMPorts()

        menu_ports = []

        for port in port_list:
            port_name = port["port"]
            menu_ports.append({'caption': port_name,
                               'command': 'select_port',
                               'checkbox': True,
                               'args': {'id_port': port_name}})

        menu_preset[0]['children'][0]['children'] = menu_ports

        serial_menu_path = DeviotPaths.setDeviotMenuPath('serial')
        serial_menu = JSONFile(serial_menu_path)
        serial_menu.setData(menu_preset)
        serial_menu.saveData()

    def createMainMenu(self):
        """Main menu

        Creates the main menu with the differents options
        including boards, libraries, COM ports, and user
        options.
        """
        self.createSerialPortsMenu()

        boards = self.createBoardsMenu()

        main_file_path = DeviotPaths.getMainJSONFile()
        menu_file = JSONFile(main_file_path)
        menu_data = menu_file.data[0]

        for fist_menu in menu_data:
            for second_menu in menu_data[fist_menu]:
                if 'children' in second_menu:
                    if(second_menu['id'] == 'initialize'):
                        second_menu['children'] = boards

        # to format purposes
        menu_data = [menu_data]

        main_user_file_path = DeviotPaths.setDeviotMenuPath()
        file_menu = JSONFile(main_user_file_path)
        file_menu.setData(menu_data)
        file_menu.saveData()


class Preferences(JSONFile):
    """Preferences

    Class to handle the preferences of the plugin

    Extends:
            JSONFile
    """

    def __init__(self):
        """Construct

        Path loads the file where the preferences are stored,
        Doing that you avoid to pass the path every time you
        need to get or set any preference.
        """
        path = DeviotPaths.getPreferencesFile()
        super(Preferences, self).__init__(path)

    def set(self, key, value):
        """Set value

        Save a value in the preferences file using a list and
        dictionaries.

        Arguments:
                key {string} -- identifier of the preference
                value {[type]} -- value of the preference
        """
        self.data[key] = value
        self.saveData()

    def get(self, key, default_value=False):
        """Get Value

        Get a value in the preferences file stored as a list and
        dictionaries format.

        Arguments:
                key {string} -- identifier of the preference

        Keyword Arguments:
                default_value {string} -- if there is none value stored
                you can set a default value (default: False)

        Returns:
                {string} -- Value of the preference
        """
        value = self.data.get(key, default_value)
        return value

    def boardSelected(self, board_id):
        """Choosed board

        Add or delete the board selected from the preferences
        files. The boards are formated in a dictionary in the
        the list 'board id'

        Arguments:
                board_id {string} -- identifier if the board selected
        """
        file_data = self.get('board_id', '')

        if(file_data):
            if board_id in file_data:
                self.data.setdefault('board_id', []).remove(board_id)
            else:
                self.data.setdefault('board_id', []).append(board_id)
            self.saveData()
        else:
            self.set('board_id', [board_id])

    def checkBoard(self, board_id):
        """Is checked

        Check if is necessary to mark or unmark the board selected

        Arguments:
                board_id {string} -- identifier of the board selected
        """
        check = False
        if(self.data):
            check_boards = self.get('board_id', '')

            if board_id in check_boards:
                check = True
        return check


class PlatformioCLI(DeviotCommands.CommandsPy):
    """Platformio

    This class handle all the request to the platformio ecosystem.
    From the list of boards to the build/upload of the sketchs.
    More info about platformio in: http://platformio.org/

    Extends:
            DeviotCommands.CommandsPy
    """

    def __init__(self, view=False):
        """Construct

        Initialize the command and preferences classes, to check
        if the current work file is an IoT type it received the view
        parameter (ST parameter). This parameter is necessary only in
        the options like build or upload.

        Keyword Arguments:
                view {st object} -- stores many info related with
                                                        ST (default: False)
        """
        self.Preferences = Preferences()
        envi_path = self.Preferences.get('CMD_ENV_PATH')
        self.Commands = DeviotCommands.CommandsPy(envi_path)
        self.view = view

        if(view):
            self.currentFilePath = DeviotPaths.getCurrentFilePath(view)
            self.cwd = DeviotPaths.getCWD(self.currentFilePath)

    def getSelectedBoards(self):
        """Selected Board(s)

        Get the board(s) list selected, from the preferences file, to
        be initialized and formated to be used in the platformio CLI

        Returns:
                {string} boards list in platformio CLI format
        """
        boards = self.Preferences.get('board_id', '')
        type_boards = ""

        if(not boards):
            return False

        for board in boards:
            type_boards += "--board=%s " % board

        return type_boards

    def initSketchProject(self):
        """CLI

        command to initialize the board(s) selected by the user. This
        function can only be use if the workig file is an IoT type
        (checked by isIOTFile)
        """
        init_boards = self.getSelectedBoards()

        if(not init_boards):
            print("None board Selected")
            return

        command = "platformio -f -c sublimetext init %s" % init_boards

        if(not isIOTFile(self.view)):
            print("This is not a IoT File")
            return

        print("Initializing the project")
        self.Commands.runCommand(command, self.cwd)

    def buildSketchProject(self):
        """CLI

        Command to build the current working sketch, it must to be IoT
        type (checked by isIOTFile)
        """
        # initialize the sketch
        self.initSketchProject()

        if(not self.Commands.error_running and isIOTFile(self.view)):
            print("Building the project")

            try:
                shutil.copy(self.currentFilePath, self.cwd + '\\src')
            except:
                print("error copying the file")
                return

            command = "platformio -f -c sublimetext run"
            self.Commands.runCommand(command, self.cwd)

            if(not self.Commands.error_running):
                print("Success")
                self.Preferences.set('builded_sketch', True)
            else:
                print("Error")
                self.Preferences.set('builded_sketch', False)

    def uploadSketchProject(self):
        """CLI

        Upload the sketch to the select board to the select COM port
        it returns an error if any com port is selected
        """
        builded_sketch = self.Preferences.get('builded_sketch', '')

        if(builded_sketch):
            id_port = self.Preferences.get('id_port', '')

            if(not id_port):
                print("None COM port selected")
                return

            command = "platformio -f -c sublimetext "
            command += "run -t upload --upload-port %s" % (id_port)
            self.Commands.runCommand(command, self.cwd)

    def cleanSketchProject(self):
        """CLI

        Delete compiled object files, libraries and firmware/program binaries
        if a sketch has been built previously
        """

        builded_sketch = self.Preferences.get('builded_sketch', '')

        if(builded_sketch):
            print("Cleaning")
            command = "platformio -f -c sublimetext run -t clean"
            self.Commands.runCommand(command, self.cwd)

            if(not self.Commands.error_running):
                self.Preferences.set('builded_sketch', False)

    def getAPICOMPorts(self):
        """CLI

        Get a JSON list with all the COM ports availables, to do it uses the
        platformio serialports command. To get more info about this fuction
        check:http://docs.platformio.org/en/latest/userguide/cmd_serialports.html
        """
        command = "platformio serialports list --json-output"
        port_list = json.loads(
            self.Commands.runCommand(command, setReturn=True))

        if(not self.Commands.error_running):
            return port_list

    def getAPIBoards(self):
        """Get boards list

        Get the boards list from the platformio API using CLI.
        to know more about platformio visit:  http://www.platformio.org/

        Returns:
                {json object} -- list with all boards in a JSON format
        """
        boards = []
        command = "platformio boards --json-output"
        boards = self.Commands.runCommand(command, setReturn=True)
        return boards


def checkEnvironPath():
    """Environment Path

    This function is used to check if the enviroment PATH  is configurated
    when the preferences files is found and seems to be right, it deletes
    the setup menu

    """

    new_menu_path = DeviotPaths.setDeviotMenuPath()
    CMD_ENV_PATH = Preferences().get('CMD_ENV_PATH', '')
    install_menu_path = DeviotPaths.getRequirenmentMenu()

    if(not os.path.exists(CMD_ENV_PATH)):

        # Create prefences file
        Preferences().set('CMD_ENV_PATH', 'YOUR-ENVIRONMENT-PATH-HERE')
        return False

    # Remove requirement menu
    if(os.path.exists(CMD_ENV_PATH)):
        if(os.path.exists(install_menu_path)):
            os.remove(install_menu_path)

        # Creates new menu
        if(not os.path.exists(new_menu_path)):
            Menu().createMainMenu()


def isIOTFile(view):
    """IoT File

    Check if the file in the current view of ST is an allowed
    IoT file, the files are specified in the exts variable.

    Arguments:
            view {st object} -- stores many info related with ST
    """
    exts = ['ino', 'pde', 'cpp', 'c', '.S']
    file_name = view.file_name()

    if file_name and file_name.split('.')[-1] in exts:
        return True
    return False


def setStatus(view):
    """Status bar

    Set the info to show in the status bar of Sublime Text.
    This info is showing only when the working file is considered IoT

    Arguments:
            view {st object} -- stores many info related with ST
    """
    info = []

    if isIOTFile(view):
        info.append('Deviot ' + getVersion())
        full_info = " | ".join(info)

        view.set_status('Deviot', full_info)


def getVersion():
    """Plugin Version

    Get the current version of the plugin stored in the preferences file.

    Returns:
            {String} -- Version of the file (only numbers)
    """
    return Preferences().get('plugin_version')


def setVersion(version):
    """Plugin Version

    Save the current version of the plugin in the preferences file.

    Returns:
            {String} -- Version of the file (only numbers)
     """
    Preferences().set('plugin_version', version)

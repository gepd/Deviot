#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sublime
from glob import glob

from ..platformio.project_recognition import ProjectRecognition
from .quick_panel import quick_panel
from .paths import getBoardsFileDataPath
from .tools import get_setting, save_setting, save_sysetting
from .preferences_bridge import PreferencesBridge
from .serial import serial_port_list
from .I18n import I18n

_ = None

class QuickMenu(PreferencesBridge):
    def __init__(self):
        super(QuickMenu, self).__init__()
        self.index = 0
        self.quick_list = []
        self.deeper = 0

        global _
        _ = I18n().translate

    def set_list(self, quick_list):
        """Set List

        Set the list with the items to be shown in the
        quick panel

        Arguments:
            quick_list {list} -- list of items
        """
        self.quick_list = quick_list

    def show_quick_panel(self, callback):
        """Quick Panel

        Show the quick panel with the given items, previously setted
        in the quick_list object. The callback can set the index
        object to selected an item when the panel is called.

        Arguments:
            callback {obj} -- callback to call after the selection
        """
        quick_panel(self.quick_list, callback, index=self.index)

    def callback_board(self, selected):
        """Board Callback
        
        The quick panel returns the index of the option selected,
        this index is used to get the id of the board and the id
        is stored in the setting file.

        last_action is used to run the compilation or upload if was
        the action before call the list of boards
        
        Arguments:
            selected {int} -- index of the selected board
        """
        if(selected == -1):
            save_sysetting('last_action', None)
            return

        boards_list = self.boards_list()
        board_select = boards_list[selected][-1]
        board_id = board_select.split("|")[-1].strip()

        self.save_selected_board(board_id)
        self.run_last_action()
        self.set_status_information()

    def boards_list(self):
        """Boards List
        
        PlatformIO returns a JSON list with all information of the boards,
        the quick panel requires a list with a different format. We will only
        show the name (caption), id and vendor.
        
        Returns:
            list -- boards list
        """
        from .file import File

        selected_boards = self.get_selected_boards()
        boards_path = getBoardsFileDataPath()
        boards_file = File(boards_path)
        boards = boards_file.read_json()
        boards_list = []
        start = ''

        for board in boards:
            id = board['id']
            vendor = board['vendor']

            if(id in selected_boards):
                start = '* ' 
            else:
                start = ''               

            caption = start + board['name']
            extra = "%s | %s" % (vendor, id)
            boards_list.append([caption, extra])

        return boards_list

    def callback_environment(self, selected):
        """Environment Callback
        
        Callback to store the select environment

        last_action is used to run the compilation or upload if was
        the action before call the list of environments
        
        Arguments:
            selected {int} -- option selected (index)
        """
        if(selected == -1):
            save_sysetting('last_action', None)
            return

        environments_list = self.environment_list()
        environment_select = environments_list[selected][1]
        environment = environment_select.split("|")[-1].strip()

        self.save_environment(environment)
        self.run_last_action()
        self.set_status_information()

    def environment_list(self):
        """
        gets a list with all selected environments and format it
        to be shown in the quick panel
        """
        from .file import File

        environments_list = []
        boards = self.boards_list()
        environments = self.get_selected_boards()
        environment = self.get_environment()
        new_environments = environments

        index = 0
        total = len(environments)
        count = total

        if(environments):
            for value in boards:
                data = value[1].split("|")
                caption = value[0][2:]
                id = data[1].strip()
                vendor = data[0].strip()

                for listed in environments:
                    if(listed == id):
                        vendor = "%s | %s" % (vendor, id)
                        environments_list.append([caption, vendor])
                        new_environments.remove(listed)
                        count -= 1

                        if(environment == listed):
                            self.index = index

                        index += 1

                if(not count):
                    break

        if(new_environments):
            for board in new_environments:
                caption = board
                vendor = "Unknown | {0}".format(board)
                environments_list.append([caption, vendor])

        return environments_list

    def callback_overwrite_baud(self, selected):
        """Baud rate callback
        
        Stores the option selected in the preferences file
        
        Arguments:
            selected {int} -- index of the selected baud rate
        """
        if(selected == -1):
            return

        selected = self.quick_list[selected]
        selected = None if selected == 'None' else selected

        save_setting('upload_speed', selected)

    
    def overwrite_baud_list(self):
        """Baud rate list
        
        List of baud rates used to overwrite the upload speed
        
        Returns:
            list -- list of baud rates
        """
        current = get_setting('upload_speed', "None")
        items = QuickMenu.baudrate_list()
        self.index = items.index(current)

        return items

    def callback_serial_ports(self, selected):
        """Selected Port Callback
        
        Stores the selected serial port in the preferences file
        
        Arguments:
            selected {str} -- Port selected ex. 'COM1'
        """
        if(selected <= 0):
            save_sysetting('last_action', None)
            return

        if(selected == 1):
            self.window.run_command('deviot_set_ip')
            return

        port_selected = self.quick_list[selected][1]
        save_setting('port_id', port_selected)

        self.run_last_action()
        self.set_status_information()

    def serial_list(self):
        """Serial Port List
        
        Gets the list of serial ports and mdns services and
        return it
        
        Returns:
            list -- available serial ports/mdns services
        """
        index = 2
        header = _("select_port_list").upper()
        ports_list = self.get_ports_list()
        ports_list.insert(0, [header])
        ports_list.insert(1, [_("menu_add_ip")])
        current = get_setting('port_id', None)   

        if(len(ports_list) < 2):
            ports_list = [_("menu_no_serial_mdns").upper()]

        for port in ports_list[2:]:
            if(current in port):
                self.index = index
            index += 1

        return ports_list

    def language_list(self):
        """Language List
        
        Builts the list with the available languages in Deviot
        
        Returns:
            list -- English language / Language String list
        """

        i18n = I18n()
        index = 0
        language_list = []
        lang_ids = i18n.get_lang_ids()
        current = get_setting('lang_id', 'en')

        for lang_id in lang_ids:
            language = i18n.get_lang_name(lang_id)
            language_list.append([language[1], language[0]])

            if(current == lang_id):
                self.index = index

            index += 1

        return language_list

    def callback_language(self, selected):
        """Language Callback
        
        Stores the user language selection
        
        Arguments:
            selected {int} -- user selection
        """
        if(selected == -1):
            return

        from .top_menu import TopMenu
        
        lang_ids = I18n().get_lang_ids()
        port_selected = lang_ids[selected]
        
        save_setting('lang_id', port_selected)
        save_setting('compile_lang', True)
        self.window.run_command("deviot_reload")

    def callback_import(self, selected):
        """Import Callback
        
        After select the library it will be inserted by the insert_libary
        command, it will include the path of the library to includes
        
        Arguments:
            selected {int} -- user index selection
        """
        if(selected <= 0):
            return

        libraries_list = self.import_list()
        library_import = libraries_list[selected][1]

        window = sublime.active_window()
        window.run_command('deviot_insert_library', {'path': library_import})

    def import_list(self):
        """Import List
        
        To generate the list of libraries, it search first in the two main folder of the plugin
        the first one in '~/.platformio/packages', that folder contain the libraries includes by default
        by each platform (avr, expressif, etc). The second folder is located in '~/platformio/lib' there
        are stored all the libraries installed by the user from the management libraries
        
        Returns:
            [list] -- quick panel list with libraries
        """
        from .libraries import get_library_list

        platform = self.get_platform()
        platform = platform if(platform) else "all"

        quick_list = get_library_list(platform=platform)
        quick_list.insert(0, [_("select_library").upper()])

        if(len(quick_list) <= 1):
            quick_list = [[_("menu_no_libraries")]]

        return quick_list

    def quick_libraries(self):
        """List of libraries
        
        Show the list of libraries availables. The callback will show
        the list of examples.
        """
        from .libraries import get_library_list
        
        platform = self.get_platform()
        platform = platform if(platform) else "all"

        self.quick_list = get_library_list(example_list=True, platform=platform)
        self.quick_list.insert(0, [_("select_library").upper()])

        if(len(self.quick_list) <= 1):
            self.quick_list = [[_("menu_no_examples")]]

        self.show_quick_panel(self.callback_library)

    def callback_library(self, selected):
        """Show Examples
        
        After the previous selection of the library, here will be search
        all folders inside of the "example" folder and will be considerated
        an example to open
        
        Arguments:
            selected {int} -- user index selection
        """
        if(selected <= 0):
            return

        library_path = self.quick_list[selected][1]
        
        if('examples' not in library_path):
            library_path = os.path.join(library_path, 'examples')

        if(self.open_file(library_path)):
            return

        library_path = os.path.join(library_path, '*')
        self.quick_list = [[_("select_example").upper()]]

        for files in glob(library_path):
            caption = os.path.basename(files)
            self.quick_list.append([caption, files])

        self.show_quick_panel(self.callback_library)

    def serial_baudrate_list(self):
        """Serial Baudrate
        
        List of baud rates to use with the serial monitor.
        It check if there is already an option selected and
        set it in the index object.
        
        Returns:
            [list] -- list of
        """
        current = get_setting('baudrate', "9600")
        items = QuickMenu.baudrate_list()

        try:
            self.index = items.index(current)
        except ValueError:
            self.index = 0

        return items

    def callback_serial_baudrate(self, selected):
        """Serial baud rate callback
        
        callback to select the baud rate used in the serial
        monitor. The option is stored in the preferences file
        
        Arguments:
            selected {int} -- index of the selected baud rate
        """
        if(selected == -1):
            return

        selected = self.quick_list[selected]
        selected = None if selected == 'None' else selected

        save_setting('baudrate', selected)

    def line_endings_list(self):
        """Serial ending strings

        List of ending string used in the monitor serial
        """
        items = [
                ["None"],
                ["New Line", "\n"],
                ["Carriage Return", "\r"],
                ["Both NL & CR", "\r\n"]
                ]
        current = get_setting('line_ending', None)
        
        simplified = [i[1] for i in items if len(i) > 1]
        simplified.insert(0, None)

        self.index = simplified.index(current)

        return items

    def callback_line_endings(self, selected):
        """Callback line endings
        
        Stores the line ending selected by the user
        
        Arguments:
            selected {int} -- index user selection
        """
        if(selected == -1):
            return

        try:
            selected = self.quick_list[selected][1]
        except IndexError:
            selected = None

        save_setting('line_ending', selected)

    def display_mode_list(self):
        """Display modes
        
        List of display modes
        """
        items = [["Text"],["ASCII"],["HEX"],["Mix"]]

        current = get_setting('display_mode', 'Text')
        self.index = items.index([current])

        return items

    def callback_display_mode(self, selected):
        """Display mode callback
        
        Stores the display mode selected by the user
        
        Arguments:
            selected {int} -- index user selection
        """
        if(selected == -1):
            return

        selected = self.quick_list[selected][0]
        save_setting('display_mode', selected)

    @staticmethod
    def baudrate_list():
        """Baudrate list

        List of baud rates shown in the monitor serial and upload speed
        quick panels.
        """
        baudrate_list = ["None",
                        "1200", 
                        "1800", 
                        "2400", 
                        "4800", 
                        "9600", 
                        "19200", 
                        "38400", 
                        "57600", 
                        "115200", 
                        "230400", 
                        "460800", 
                        "500000", 
                        "576000",
                        "921600", 
                        "1000000", 
                        "1152000"]

        return baudrate_list

    def open_file(self, sketch_path):
        """Open sketch
        
        search in the given path a ino or pde file extension
        and open it in a new windows when it's found
        
        Arguments:
            sketch_path {str} -- path (file/folder) where to search
        Returns:
            [bool] -- true if it open file, false if not
        """
        window = sublime.active_window()

        if(sketch_path.endswith(('.ino', '.pde'))):
            window.open_file(sketch_path)
            return True

        for file in os.listdir(sketch_path):
            if(file.endswith(('.ino', '.pde'))):
                file = os.path.join(sketch_path, file)
                window.open_file(file)
                return True
        return False

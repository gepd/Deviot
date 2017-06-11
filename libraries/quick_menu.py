#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..platformio.project_recognition import ProjectRecognition
from .quick_panel import quick_panel
from . import paths
from .tools import get_setting, save_setting
from .preferences_bridge import PreferencesBridge 


class QuickMenu(PreferencesBridge):
    def __init__(self):
        super(QuickMenu, self).__init__()
        self.index = 0

    def quick_boards(self):
        """Boards Menu
        
        Shows the quick panel with the availables boards in
        deviot
        """
        boards_list = self.quick_boards_list()
        quick_panel(boards_list, self.callback_board)

    def callback_board(self, selected):
        """Board Callback
        
        The quick panel returns the index of the option selected,
        this index is used to get the id of the board and the id
        is stored in the setting file
        
        Arguments:
            selected {int} -- index of the selected board
        """
        if(selected == -1):
            return

        boards_list = self.quick_boards_list()
        board_select = boards_list[selected][-1]
        board_id = board_select.split("|")[-1].strip()

        self.save_selected_board(board_id)

    def quick_boards_list(self):
        """Boards List
        
        PlatformIO returns a JSON list with all information of the boards,
        the quick panel requires a list with a different format. We will only
        show the name (caption), id and vendor.
        
        Returns:
            list -- boards list
        """
        from .file import File

        selected_boards = self.get_selected_boards()
        boards_path = paths.getBoardsFileDataPath()
        boards_file = File(boards_path)
        boards = boards_file.read_json()
        boards_list = []

        for board in boards:
            id = board['id']
            vendor = board['vendor']

            if(id in selected_boards):
                start = '- '
            else:
                start = '+ '

            caption = start + board['name']
            extra = "%s | %s" % (vendor, id)
            boards_list.append([caption, extra])

        return boards_list

    def quick_environments(self):
        """Environment Panel
        
        Displays the quick panel with the available environments
        """
        environments_list = self.quick_environment_list()
        quick_panel(environments_list, self.callback_environment, index=self.index)

    def callback_environment(self, selected):
        """Environment Callback
        
        Callback to store the select environment
        
        Arguments:
            selected {int} -- option selected (index)
        """
        if(selected == -1):
            return

        environments_list = self.quick_environment_list()
        environment_select = environments_list[selected][1]
        environment = environment_select.split("|")[-1].strip()

        self.save_environment(environment)

    def quick_environment_list(self):
        """
        gets a list with all selected environments and format it
        to be shown in the quick panel
        """
        from .file import File

        environments_list = []
        boards = self.quick_boards_list()
        environments = self.get_selected_boards()
        environment = self.get_environment()

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
                        count -= 1

                        if(environment == listed):
                            self.index = index

                        index += 1

                if(not count):
                    break

        return environments_list

    def quick_serial_ports(self):
        """List of Serial Ports
        
        Show the list of serial ports availables in the quick panel
        """
        port_list = serial_port_list()
        quick_panel(port_list, self.callback_serial_ports)

    def callback_serial_ports(self, selected):
        """Selected Port Callback
        
        Stores the selected serial port in the preferences file
        
        Arguments:
            selected {str} -- Port selected ex. 'COM1'
        """
        if(selected == -1):
            return

        port_list = serial_port_list()
        port_selected = port_list[selected][1]
        
        save_setting('port_id', port_selected)

    def quick_language(self):
        """Language Panel
        
        Shows the panel to selecte the language of the plugin
        """
        language_list = self.quick_language_list()
        quick_panel(language_list, self.callback_language, index=self.index)

    def quick_language_list(self):
        """Language List
        
        Builts the list with the available languages in Deviot
        
        Returns:
            list -- English language / Language String list
        """
        from .I18n import I18n

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

        from .I18n import I18n
        from .top_menu import TopMenu
        
        lang_ids = I18n().get_lang_ids()
        port_selected = lang_ids[selected]
        
        save_setting('lang_id', port_selected)
        save_setting('compile_lang', True)
        self.window.run_command("deviot_reload")
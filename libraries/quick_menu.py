#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..platformio.project_recognition import ProjectRecognition
from .quick_panel import quick_panel
from . import paths, tools
from ..platformio.pio_bridge import PioBridge 


class QuickMenu(PioBridge):

    def __init__(self):
        super(QuickMenu, self).__init__()

    def boards_menu(self):
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

        file_hash = self.get_file_hash()
        settings = tools.get_setting(file_hash, [])

        boards_list = self.quick_boards_list()
        board_select = boards_list[selected][-1]
        board_id = board_select.split("|")[-1].strip()

        if(not settings):
            settings = {}
        
        if('boards' not in settings):
            settings['boards'] = []
            settings['boards'].append(board_id)
        else:
            if(board_id not in settings['boards']):
                settings['boards'].append(board_id)
            else:
                settings['boards'].remove(board_id)

        tools.save_setting(file_hash, settings)

    def quick_boards_list(self):
        """Boards List
        
        PlatformIO returns a JSON list with all information of the boards,
        the quick panel requires a list with a different format. We will only
        show the name (caption), id and vendor.
        
        Returns:
            list -- boards list
        """
        from .file import File

        envs = self.get_environments()
        boards_path = paths.getBoardsFileDataPath()
        boards_file = File(boards_path)
        boards = boards_file.read_json()
        boards_list = []

        for board in boards:
            id = board['id']
            vendor = board['vendor']

            if(id in envs):
                start = '- '
            else:
                start = '+ '

            caption = start + board['name']
            extra = "%s | %s" % (vendor, id)
            boards_list.append([caption, extra])

        return boards_list

    def environment_menu(self):
        """Environment Panel
        
        Displays the quick panel with the available environments
        """
        environments_list = self.quick_environment_list()
        quick_panel(environments_list, self.callback_environment)

    def callback_environment(self, selected):
        """Environment Callback
        
        Callback to store the select environment
        
        Arguments:
            selected {int} -- option selected (index)
        """
        if(selected == -1):
            return

        file_hash = self.get_file_hash()
        settings = tools.get_setting(file_hash)
        environments_list = self.quick_environment_list()
        environment_select = environments_list[selected][1]
        environment = environment_select.split("|")[-1].strip()

        if(not settings):
            settings = {}

        settings['select_environment'] = environment
        tools.save_setting(file_hash, settings)

    def quick_environment_list(self):
        """
        gets a list with all selected environments and format it
        to be shown in the quick panel
        """
        from .file import File

        environments_list = []
        boards = self.quick_boards_list()
        environments = self.get_envs_initialized()

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
                
                if(not count):
                    break

        return environments_list
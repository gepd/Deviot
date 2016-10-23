#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..platformio.project_recognition import ProjectRecognition
from .quick_panel import quick_panel
from ..libraries import paths, tools
import json


class Menu(object):

    def __init__(self):
        self.PR = ProjectRecognition()

    def quick_boards_list(self):
        """
        gets a list with all available boards
        """
        from .file import File

        envs = self.PR.get_envs()
        boards_path = paths.getBoardsFilePath()
        boards_file = File(boards_path)
        boards = boards_file.get_in_json()
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

    def boards_menu(self):
        """
        show the quick panel with the selected environments
        """
        boards_list = self.quick_boards_list()
        quick_panel(boards_list, self.callback_board)
        boards_list = self.quick_boards_list()

    def callback_board(self, selected):
        """
        callback to store the selected board
        """
        if(selected == -1):
            return

        file_hash = self.PR.get_project_hash()
        file_config = tools.get_config(file_hash)
        boards_list = self.quick_boards_list()
        board_select = boards_list[selected][-1]
        board = board_select.split("|")[-1].strip()

        if(not file_config):
            config = tools.get_config(full=True)
            config[file_hash] = {}
            config[file_hash]['boards'] = [board]
            tools.save_config(full=config)
            return 200

        if(board not in file_config['boards']):
            file_config['boards'].append(board)
        else:
            file_config['boards'].remove(board)

        tools.save_config(file_hash, file_config)

    def quick_environment_list(self):
        """
        gets a list with all selected environments and format it
        to be shown in the quick panel
        """
        from .file import File

        envs = self.PR.get_envs()
        boards_path = paths.getBoardsFilePath()
        boards_file = File(boards_path)
        environments_list = []

        boards = boards_file.get_in_json()

        for value in boards:
            id = value['id']
            caption = value['name']
            vendor = value['vendor']

            for listed in envs:
                if(listed == id):
                    vendor = "%s | %s" % (vendor, id)
                    environments_list.append([caption, vendor])

        return environments_list

    def environment_menu(self):
        """
        show the quick panel with the selected environments
        """
        environments_list = self.quick_environment_list()
        quick_panel(environments_list, self.callback_environment)

    def callback_environment(self, selected):
        """
        callback to store the selected environment
        """
        if(selected == -1):
            return

        file_hash = self.PR.get_project_hash()
        file_config = tools.get_config(file_hash)
        environments_list = self.quick_environment_list()
        environment_select = environments_list[selected][1]
        environment = environment_select.split("|")[-1].strip()

        if(not file_config):
            config = tools.get_config(full=True)
            config[file_hash] = {}
            config[file_hash]['select_environment'] = environment
            tools.save_config(full=config)
            return 200

        file_config['select_environment'] = environment
        tools.save_config(file_hash, file_config)

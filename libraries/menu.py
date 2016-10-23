#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..platformio.project_recognition import ProjectRecognition
from .quick_panel import quick_panel
from ..libraries import paths, tools
import json


class Menu(object):

    def __init__(self):
        self.PR = ProjectRecognition()

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
        quick_panel(environments_list, self.save_environment)

    def save_environment(self, selected):
        """
        callback to store the selected environment
        """
        if(selected == -1):
            return

        environment_config = tools.get_config('environment_selected')
        environments_list = self.quick_environment_list()
        environment_select = environments_list[selected][1]
        environment = environment_select.split("|")[-1].strip()
        file_name = self.PR.get_project_file_name(ext=False)

        if(not environment_config):
            config = tools.get_config(full=True)
            config['environment_selected'] = {}
            config['environment_selected'][file_name] = environment
            tools.save_config(full=config)
            return 200

        environment_config[file_name] = environment
        tools.save_config('environment_selected', environment_config)

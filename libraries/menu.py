#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..platformio.project_recognition import ProjectRecognition
from ..libraries import paths, tools
import json


class Menu(object):

    def __init__(self):
        self.PR = ProjectRecognition()

    def environment_menu(self):
        """
        gets a list with all selected environments
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

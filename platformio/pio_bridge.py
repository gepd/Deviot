#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

from .run_command import run_command
from ..libraries import paths
from ..libraries.file import File
from ..libraries.tools import get_setting
from .project_recognition import ProjectRecognition

class PioBridge(ProjectRecognition):
    def __init__(self):
        super(PioBridge, self).__init__()

    def save_boards_list(self):
        """PlatformIO Board List
        
        Gets the list of all boards availables in platformIO and
        stores it in a json file
        """
        cmd = ['boards', '--json-output']
        boards = run_command(cmd, set_return=True)

        board_file_path = paths.getBoardsFileDataPath()
        File(board_file_path).write(boards)

    def get_boards_list(self):
        """Board List
        
        Get the json file with the list of boards and return it.
        The location of the json file is defined in paths.py in the
        function getBoardsFileDataPath
        
        Returns:
            json -- list of boards
        """
        board_file_path = paths.getBoardsFileDataPath()

        file = File(board_file_path)
        boards_list = file.read_json(boards)

        return boards_list

    def get_environments(self):
        """Environments
        
        List of all environments in the projects the list includes
        the one selected in deviot and the one initialized in the
        platformio.ini file and mixed excluding the duplicates
        
        Returns:
            list -- list of environments
        """
        file_hash = self.get_file_hash()
        settings = get_setting(file_hash, [])
        environments = self.get_envs_initialized()

        if(settings and settings['boards']):
            boards = settings['boards']
            environments = list(set(environments) | set(boards))

        return environments

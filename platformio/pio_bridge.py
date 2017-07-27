#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import os
from glob import glob

from ..libraries import paths
from ..libraries.file import File
from ..libraries.tools import get_setting
from .command import Command

class PioBridge(Command):
    def __init__(self):
        super(PioBridge, self).__init__()

        self.cwd = self.get_working_project_path()

    def save_boards_list(self):
        """PlatformIO Board List
        
        Gets the list of all boards availables in platformIO and
        stores it in a json file
        """
        self.cwd = None
        self.set_return = True
        self.realtime = False
        
        cmd = ['boards', '--json-output']
        boards = self.run_command(cmd)

        board_file_path = paths.getBoardsFileDataPath()
        File(board_file_path).write(boards)

    def save_boards_list_async(self):
        """Save boards list async
        
        Stores the board list file in a new thread to avoid
        block the Sublime Text UI
        """
        from threading import Thread
        from ..libraries.thread_progress import ThreadProgress
        from ..libraries.I18n import I18n

        txt = I18n().translate('processing')

        thread = Thread(target=self.save_boards_list)
        thread.start()
        ThreadProgress(thread, txt, '')


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

    def remove_ini_environment(self, board_id):
        """Remove Environment
        
        Removes the environments from the platformio.ini file.
        It happens each time a environment/board is removed selecting it
        from the list of boards (Select Board). The behavior of this
        option is; if the board isn't in the configs, it will be added
        if not, removed.
        
        Arguments:
            board_id {[type]} -- [description]
        """
        if(self.is_initialized):

            key = 'env:' + board_id
            pio_file = self.get_config(full=True)

            if(key in pio_file):
                pio_file.pop(key, None)

            self.save_config(pio_file, full=True)

    def get_working_project_path(self):
        """Working Path
        
        The working path is where platformio.ini is located
        it's used each time when deviot is compiling the code

        Returns:
            str -- path/working_path
        """
        pio_structure = self.get_structure_option()

        if(pio_structure):
            project_path = self.get_project_path()
            
            if(not project_path):
                return None

            if('src' in project_path):
                project_path = self.get_parent_path()
            return project_path

        if(self.is_initialized()):
            ini_path = self.get_ini_path()
            working_path = os.path.dirname(ini_path)
            return working_path
        
        return self.get_temp_project_path()

    def get_config(self, key=None, default=None, full=False):
        """Gets platformio.ini Configs
        
        Gets the platformio.ini file of the project loaded in the
        current view and return the value of the key requested.
        You can use the full parameter to retrieve the full file
        
        Keyword Arguments:
            key {str} -- key of the option (default: {None})
            default {str} -- default value if the key value
                             is not found (default: {None})
            full {bool} -- to return the full file (default: {False})
        
        Returns:
            str -- found or default value
        """
        from ..libraries.configobj.configobj import ConfigObj

        file_config = self.get_ini_path()
        config = ConfigObj(file_config)

        if(full):
            return config

        if(key in config):
            return config[key]
        return default


    def save_config(self, key=None, value=None, full=False):
        """Save in platformio.ini
        
        Stores the key and value in platfirmio.ini file, this
        file is the one asociated with current open sketch
        
        Keyword Arguments:
            key {str} -- key of the option/config (default: {None})
            value {str} -- value of the option/config (default: {None})
            full {bool} -- when is true write key in the file (default: {False})
        
        Returns:
            bool -- True if the file was write, False if not
        """
        from ..libraries.configobj.configobj import ConfigObj

        file_config = self.get_ini_path()
        config = ConfigObj(file_config)

        if(full):
            key.write()
            return True

        config[key] = value
        
        config.write()
        return True

    def get_structure_option(self):
        """Pio Structure Option
        
        Check if the platformio structure option is mark as
        true or not
        
        Returns:
            bool -- true to keep working with platformio structure
        """

        return get_setting('pio_structure', False)

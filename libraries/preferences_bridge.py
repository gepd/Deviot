#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

from .tools import get_setting, save_setting
from ..platformio.pio_bridge import PioBridge 

class PreferencesBridge(PioBridge):
    def __init__(self):
        super(PreferencesBridge, self).__init__()

    def save_selected_board(self, board_id):
        """Store Board
        
        Stores the given board in the preferences file, if the board
        is already in the file, it will be removed
        
        Arguments:
            board_id {str} -- id of the board ex. 'uno'
        """
        file_hash = self.get_file_hash()
        settings = get_setting(file_hash, {})
        save_flag = True
        
        if('boards' not in settings):
            settings['boards'] = []
            settings['boards'].append(board_id)
        else:
            if(board_id not in settings['boards']):
                settings['boards'].append(board_id)
            else:
                settings['boards'].remove(board_id)
                self.remove_ini_environment(board_id)
                save_flag = False

        save_setting(file_hash, settings)
        
        if(save_flag):
            self.save_environment(board_id)

    def get_selected_boards(self):
        """Get Board/s
        
        List of all boards in the project, the list includes
        the one selected in deviot, and the one initialized in the
        platformio.ini file, they're mixed and excluding the duplicates
        
        Returns:
            list -- list of boards
        """
        file_hash = self.get_file_hash()
        settings = get_setting(file_hash, [])
        boards = self.get_envs_initialized()

        if('boards' in settings):
            extend_boards = settings['boards']
            extend_boards.extend(boards)
            extend_boards = list(set(extend_boards))
            boards = extend_boards

        return boards

    def save_environment(self, board_id):
        """Save Environment
        
        Stores the environment/board selected to work with.
        This board will be used to compile the sketch
        
        Arguments:
            board_id {str} -- id of the board ex. 'uno'
        """
        file_hash = self.get_file_hash()
        settings = get_setting(file_hash, {})
        settings['select_environment'] = board_id
        save_setting(file_hash, settings)

    def get_environment(self):
        """Get Environment
        
        Get the environment selected for the project/file in the current view
        
        Returns:
            str -- environment/board id ex. 'uno'
        """
        file_hash = self.get_file_hash()
        settings = get_setting(file_hash, {})

        if('select_environment' in settings):
            return settings['select_environment']

    def get_serial_port(self):
        """Serial Port Selected
        
        Get the serial port stored in the preferences file
        
        Returns:
            str -- port id ex 'COM1'
        """
        port_id = get_setting('port_id', '')
        
        return port_id
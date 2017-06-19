#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

from .tools import get_setting, save_setting
from ..platformio.pio_bridge import PioBridge
from .configobj.configobj import ConfigObj

class PreferencesBridge(PioBridge):
    # Flags to be used with last action feature
    COMPILE = 1
    UPLOAD = 2

    def __init__(self):
        super(PreferencesBridge, self).__init__()

    def save_selected_board(self, board_id):
        """Store Board
        
        Stores the given board in the preferences file, if the board
        is already in the file, it will be removed
        
        Arguments:
            board_id {str} -- id of the board ex. 'uno'
        """
        settings = get_setting('boards', [])
        save_flag = True
        
        if(not settings):
            settings.append(board_id)
        else:
            if(board_id not in settings):
                settings.append(board_id)
            else:
                settings.remove(board_id)
                
                if(len(settings) > 0):
                    board_id = settings[-1]
                else:
                    board_id = ''

        save_setting('boards', settings)
        
        self.save_environment(board_id)

    def get_selected_boards(self):
        """Get Board/s
        
        List of all boards in the project, the list includes
        the one selected in deviot, and the one initialized in the
        platformio.ini file, they're mixed and excluding the duplicates
        
        Returns:
            list -- list of boards
        """
        settings = get_setting('boards', [])
        boards = self.get_envs_initialized()

        if(boards):
            settings.extend(boards)

        return settings

    def save_environment(self, board_id):
        """Save Environment
        
        Stores the environment/board selected to work with.
        This board will be used to compile the sketch
        
        Arguments:
            board_id {str} -- id of the board ex. 'uno'
        """
        save_setting('select_environment', board_id)

    def get_environment(self):
        """Get Environment
        
        Get the environment selected for the project/file in the current view
        
        Returns:
            str -- environment/board id ex. 'uno'
        """
        settings = get_setting('select_environment', None)

        return settings

    def get_serial_port(self):
        """Serial Port Selected
        
        Get the serial port stored in the preferences file
        
        Returns:
            str -- port id ex 'COM1'
        """
        port_id = get_setting('port_id', None)
        
        return port_id

    def run_last_action(self):
        """Last Action
        
        If the user start to compile or upload the sketch and none board or port
        is selected, the quick panel is displayed to select the corresponding option.
        As the quick panel is a async method, the compilation or upload will not
        continue. Before upload or compile a flag is stored to what run after the selection
        """

        last_action = get_setting('last_action', None)

        if(last_action == self.COMPILE):
            from ..platformio.compile import Compile
            Compile()
        elif(last_action == self.UPLOAD):
            from ..platformio.upload import Upload
            Upload()

    def programmer(self):
        """Programmer

        Adds the programmer strings in the platformio.ini file, it considerate
        environment and programmer selected

        Arguments:
            programmer {str} -- id of chosen option
        """

        # list of programmers

        programmer = get_setting('programmer_id', None)
        ini_path = self.get_ini_path()

        flags = {
            'avr':          {"upload_protocol": "stk500v1",
                             "upload_flags": "-P$UPLOAD_PORT",
                             "upload_port": self.port_id},
            'avrmkii':      {"upload_protocol": "stk500v2",
                             "upload_flags": "-Pusb"},
            'usbtyni':      {"upload_protocol": "usbtiny"},
            'arduinoisp':   {"upload_protocol": "arduinoisp"},
            'usbasp':       {"upload_protocol": "usbasp",
                             "upload_flags": "-Pusb"},
            'parallel':     {"upload_protocol": "dapa",
                             "upload_flags": "-F"},
            'arduinoasisp': {"upload_protocol": "stk500v1",
                             "upload_flags": "-P$UPLOAD_PORT -b$UPLOAD_SPEED",
                             "upload_speed": "19200",
                             "upload_port": self.port_id}
        }

        # open platformio.ini and get the environment
        ini_file = ConfigObj(ini_path, list_values=False)
        environment = 'env:{0}'.format(self.board_id)

        # stop if environment wasn't initialized yet
        if(environment not in ini_file):
            return

        env = ini_file[environment]
        rm = ['upload_protocol', 'upload_flags', 'upload_speed', 'upload_port']

        # remove previous configuration
        if(rm[0] in env):
            for line in rm:
                if(line in env):
                    env.pop(line)

        # add programmer option if it was selected
        if(programmer):
            env.merge(flags[programmer])

        # save in file
        ini_file.write()

    def add_extra_library(self):
        """Add extra library folder
        
        Adds an extra folder where to search for user libraries,
        this option will run before compile the code.

        The path of the folder must be set from the option 
        `add extra folder` in the library option menu
        """
        ini_path = self.get_ini_path()
        extra = get_setting('extra_library', None)

        ini_file = ConfigObj(ini_path, list_values=False)
        environment = 'env:{0}'.format(self.board_id)

        if(environment not in ini_file):
            return

        env = ini_file[environment]

        if(not extra):
            if('lib_extra_dirs' in env):
                env.pop('lib_extra_dirs')

        if(extra):
            extra_option = {'lib_extra_dirs': extra}
            env.merge(extra_option)

        ini_file.write()
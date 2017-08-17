#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

from os import path, remove
from shutil import copyfile
from ..libraries import __version__ as version
from ..libraries.project_check import ProjectCheck
from ..libraries.messages import MessageQueue
from ..libraries.tools import save_sysetting

class Initialize(ProjectCheck):
    """
    Runs the init command to start working with a new board
    Initialize a new folder you need to know the board id
    and pass it as an argument in the class

    Initialize(board_id)

    The code will run in a new thread to avoid block the
    execution of the sublime text while platformio is working
    """
    def __init__(self):
        super(Initialize, self).__init__()

        messages = MessageQueue("_deviot_starting{0}", version)
        messages.start_print()
        
        self.dprint = messages.put
        self.derror = messages.print_once
        self.dstop = messages.stop_print

    def add_board(self):
        """New Board
        
        Adds a new board to the environments of platformio
        this new board will be stored in the platformio.ini
        file and will be use with the plugin
        
        Arguments:
            board_id {str} -- name of the board to initialize
        
        Returns:
            bool -- true if the board was succefully intilized or if it
                    was already initialized, if there was an error, false
        """

        self.check_board_selected()
        if(not self.board_id):
            return

        envs = self.get_envs_initialized()
        if(envs and self.board_id in envs):
            return True

        cmd = ['init', '-b ', self.board_id]
        self.run_command(cmd)

        self.structurize_project()

    def nonblock_add_board(self):
        """New Thread Execution
        
        Starts a new thread to run the add_board method
        
        Arguments:
            board_id {str} -- id_of the board to initialize
        """
        from threading import Thread

        thread = Thread(target=self.add_board)
        thread.start()

    def after_complete(self):
        """At complete
        
        This method will run functions after complete a compilation
        or upload an sketch. You should only put here a fuction or
        a method
        """

        # remove the cpp temporal file
        self.del_cpp_temp()

        # remove src_filter from platformio.ini
        self.exclude_ino(remove=True)

        # remove src_dir flag from platformio.ini
        self.remove_src()

        # stop message queue
        self.dstop()

        # none last action
        save_sysetting('last_action', None)

    def make_cpp_temp(self):
        """cpp file
        
        copy a ino file in a new cpp file
        """
        extension = self.get_file_extension()

        if(extension == 'ino'):
            file_path = self.get_file_path()
            cpp_file = file_path.replace('.ino', '.cpp')
            
            copyfile(file_path, cpp_file)
            self.add_arduino_lib(cpp_file)
            self.exclude_ino()

    def del_cpp_temp(self):
        """remove cpp
        
        remove the cpp file
        """
        file_path = self.get_file_path()
        ino_file = file_path.replace('.cpp', '.ino')
        cpp_file = file_path.replace('.ino', '.cpp')

        if(path.exists(cpp_file) and path.exists(ino_file)):
            remove(cpp_file)
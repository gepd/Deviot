#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

from sys import exit

from .initialize import Initialize
from ..libraries.tools import save_setting

class Compile(Initialize):
    def __init__(self):
        super(Compile, self).__init__()

        self.nonblock_compile()

    def start_compilation(self):
        """Compilation
        
        Starts the compilation command, it first checks if the file in the
        current view is a .iot file and if a board (environment) has been selected
        """

        if(not self.is_iot()):
            self.derror("not_iot_{0}", self.get_file_name())
            exit(0)

        save_setting('last_action', self.COMPILE)
        
        self.add_board()
        if(not self.board_id):
            self.derror("select_board_list")
            return

        # add extra library board
        self.add_extra_library()

        cmd = ['run', '-e ', self.board_id]
        self.run_command(cmd)

        self.dstop()
        save_setting('last_action', None)

    def nonblock_compile(self):
        """New Thread Execution
        
        Starts a new thread to run the start_compilation method
        """
        from threading import Thread

        thread = Thread(target=self.start_compilation)
        thread.start()

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

from sys import exit

from .initialize import Initialize
from .run_command import run_command

class Compile(Initialize):
    def __init__(self):
        super(Compile, self).__init__()

        self.nonblock_compile()

    def start_compilation(self):
        if(not self.is_iot()):
            exit(0)

        self.add_board()

        cmd = ['run', '-e ', self.board_id]
        out = run_command(cmd, self.cwd, realtime=True)

    def nonblock_compile(self):
        """New Thread Execution
        
        Starts a new thread to run the start_compilation method
        """
        from threading import Thread

        thread = Thread(target=self.start_compilation)
        thread.start()

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

from sys import exit

from .initialize import Initialize
from ..libraries.tools import save_sysetting
from ..libraries.thread_progress import ThreadProgress

class Compile(Initialize):
    def __init__(self):
        super(Compile, self).__init__()

        self.nonblock_compile()

    def start_compilation(self):
        """Compilation
        
        Starts the compilation command, it first checks if the file in the
        current view is a .iot file and if a board (environment) has been selected
        """
        if(not self.check_main_requirements()):
            exit(0)

        save_sysetting('last_action', self.COMPILE)
        
        self.add_board()
        if(not self.board_id):
            self.print("select_board_list")
            return

        self.add_option('lib_extra_dirs')

        # check if there is a new speed to overwrite
        self.add_option('upload_speed')

        # add src_dir option if it's neccesary
        self.override_src()

        cmd = ['run', '-e ', self.board_id]
        self.run_command(cmd)

        self.after_complete()

    def nonblock_compile(self):
        """New Thread Execution
        
        Starts a new thread to run the start_compilation method
        """
        from threading import Thread
        from ..libraries.I18n import I18n

        _ = I18n().translate

        thread = Thread(target=self.start_compilation)
        thread.start()
        ThreadProgress(thread, _('processing'), '')

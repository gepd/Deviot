#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

from sys import exit

from .initialize import Initialize
from ..libraries.tools import save_setting
from ..libraries.thread_progress import ThreadProgress
from ..libraries.I18n import I18n

_ = I18n

class Clean(Initialize):
    def __init__(self):
        super(Clean, self).__init__()

        global _
        _ = I18n().translate

        self.nonblock_clean()

    def start_cleaning(self):
        """Cleaning
        
        Starts the cleaning command. This command cleand the binary files
        in the .pioenvs folder (hidden in unix system)
        """
        if(not self.check_main_requirements()):
            exit(0)

        self.check_board_selected()
        if(not self.board_id):
            return

        envs = self.get_envs_initialized()
        if(envs and self.board_id not in envs):
            self.derror("init_not_possible")
            return

        cmd = ['run', '-t', 'clean', '-e ', self.board_id]
        self.run_command(cmd)

        self.dstop()

    def nonblock_clean(self):
        """New Thread Execution
        
        Starts a new thread to run the start_cleaning method
        """
        from threading import Thread

        thread = Thread(target=self.start_cleaning)
        thread.start()
        ThreadProgress(thread, _('processing'), '')

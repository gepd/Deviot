#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

from sys import exit

from .initialize import Initialize
from .run_command import run_command
from ..libraries.tools import save_setting

class Upload(Initialize):
    def __init__(self):
        super(Upload, self).__init__()

        save_setting('last_action', self.UPLOAD)
        self.nonblock_upload()

    def start_upload(self):
        if(not self.is_iot()):
            exit(0)

        self.check_board_selected()
        if(not self.board_id):
            return

        self.check_port_selected()
        if(not self.port_id):
            return

        cmd = ['run', '-t', 'upload', '--upload-port', self.port_id, '-e ', self.board_id]
        out = run_command(cmd, self.cwd, realtime=True)

        save_setting('last_action', None)

    def nonblock_upload(self):
        """New Thread Execution
        
        Starts a new thread to run the start_upload method
        """
        from threading import Thread

        thread = Thread(target=self.start_upload)
        thread.start()

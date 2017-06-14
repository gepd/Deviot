#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

from sys import exit

from .initialize import Initialize
from ..libraries.tools import save_setting

class Upload(Initialize):
    def __init__(self):
        super(Upload, self).__init__()

        self.nonblock_upload()

    def start_upload(self):
        """Upload
        
        Run the upload platformio command checking if a board (environment)
        and a serial port is selected
        """
        if(not self.is_iot()):
            self.derror("not_iot_{0}", self.get_file_name())
            exit(0)

        save_setting('last_action', self.UPLOAD)

        self.check_board_selected()
        if(not self.board_id):
            self.dprint("select_board_list")
            return

        self.check_port_selected()
        if(not self.port_id):
            self.dprint("select_port_list")
            return

        cmd = ['run', '-t', 'upload', '--upload-port', self.port_id, '-e ', self.board_id]
        out = run_command(cmd)

        self.dstop()
        save_setting('last_action', None)

    def nonblock_upload(self):
        """New Thread Execution
        
        Starts a new thread to run the start_upload method
        """
        from threading import Thread

        thread = Thread(target=self.start_upload)
        thread.start()

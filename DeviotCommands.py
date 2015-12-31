#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import sublime
import subprocess
import os

if(int(sublime.version()) < 3000):
    import DeviotMessages
else:
    from . import DeviotMessages


class CommandsPy(object):
    """Platformio commands

    Class to handle the different functions allowed by
    the platformio API, to know more information visit
    the web site: www.platformio.org
    """

    def __init__(self, env_path=False, console=False, cwd=None):
        super(CommandsPy, self).__init__()
        self.error_running = False
        self.message_queue = DeviotMessages.MessageQueue(console)
        self.message_queue.startPrint()
        self.cwd = cwd

        # Set the enviroment Path
        if(env_path):
            os.environ['PATH'] = env_path + os.pathsep + os.environ['PATH']

    def runCommand(self, commands, setReturn=False, verbose=False):

        if(not commands):
            return False

        options = commands[0]

        try:
            args = commands[1]
        except:
            args = ''

        command = "platformio -f -c sublimetext %s %s" % (options, args)

        process = subprocess.Popen(command, stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, cwd=self.cwd,
                                   universal_newlines=True, shell=True)

        output = process.communicate()

        stdout = output[0]
        stderr = output[1]

        return_code = process.returncode

        if(verbose):
            self.message_queue.put(stdout)

            if(stderr):
                self.message_queue.put(stderr)

        if(return_code != 0):
            self.error_running = True

        if(setReturn):
            return stdout

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import subprocess
import os


class CommandsPy(object):
    """Platformio commands

    Class to handle the different functions allowed by
    the platformio API, to know more information visit
    the web site: www.platformio.org
    """

    def __init__(self, env_path=False):
        super(CommandsPy, self).__init__()
        self.error_running = False

        # Set the enviroment Path
        if(env_path):
            os.environ['PATH'] = os.pathsep + env_path + os.environ['PATH']

    def runCommand(self, commands, cwd=None, setReturn=False, verbose=False):

        if(not commands):
            return False

        options = commands[0]

        try:
            args = commands[1]
        except:
            args = ''

        command = "platformio -f -c sublimetext %s %s" % (options, args)

        process = subprocess.Popen(command, stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, cwd=cwd,
                                   universal_newlines=True, shell=True)

        output = process.communicate()

        stdout = output[0]
        stderr = output[1]

        return_code = process.returncode

        if(verbose):
            print(stdout)
            print(stderr)

        if(return_code != 0):
            self.error_running = True

        if(setReturn):
            return stdout

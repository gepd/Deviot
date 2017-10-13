# !/usr/bin/env python
# -*- coding: utf-8 -*-

from os import getcwd, environ
import subprocess
from sys import exit

from ..libraries.tools import get_setting, get_sysetting, create_command
from ..platformio.project_recognition import ProjectRecognition

###
dprint = None
derror = None
dstop = None
###

class Command(ProjectRecognition):
    def __init__(self):
        super(Command, self).__init__()
        self.realtime = True
        self.set_return = False
        self.verbose = get_setting('verbose_output', False)
        self.dprint = None

        env_path = get_sysetting('env_path', None)
        
        if(env_path):
            environ['PATH'] = env_path

    def run_command(self, command, prepare=True):
        '''
        Run a command with Popen and return the results or print the errors
        '''

        if(not self.cwd):
            self.cwd = getcwd()

        if(prepare):
            command = self.prepare_command(command)
        command = ' '.join(command)

        process = subprocess.Popen(command, stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, cwd=self.cwd,
                                   universal_newlines=True, shell=True)

        if(self.realtime):
            while True:
                output = process.stdout.readline()
                # exit when there is nothing to show
                if output == '' and process.poll() is not None:
                    break

                if output:
                    self.dprint(output, hide_hour=True)
                    # dprint(output)

        # return code and stdout
        output = process.communicate()
        stdout = output[0]
        return_code = process.returncode

        # dstop()

        if stdout and self.set_return:
            return stdout
        
        return (return_code, stdout)

    def prepare_command(self, post_command):
        cmd = " ".join(post_command)
        command = create_command(['platformio', '-f', '-c', 'sublimetext'])
        command.extend(post_command)

        # verbose mode
        if(self.verbose and 'run' in cmd and '-e' in cmd):
            command.extend(['-v'])

        command.append("2>&1")

        return command
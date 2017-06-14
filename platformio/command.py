# !/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess
from sys import exit

from ..libraries import tools
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
        self.verbose = False
        self.dprint = None

    def run_command(self, command):
        '''
        Run a command with Popen and return the results or print the errors
        '''

        if(not self.cwd):
            self.cwd = os.getcwd()

        command = self.prepare_command(command)
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
        command = tools.create_command(['pio', '-f', '-c', 'sublimetext'])
        command.extend(post_command)

        # verbose mode
        if(self.verbose and 'run' in cmd and '-e' in cmd and 'upload' not in cmd):
            command.extend(['-vvv'])

        command.append("2>&1")
        command = ' '.join(command)

        return command

    def load_printer(self):
        self.start_print()
        
        self.print = self.put
        self.error = self.print_once
        print("finish config")

    def set_dprint(self, dprint):
        self.dprint = dprint

"""
def run_command(command, cwd=None, realtime=False, set_return=None):
    '''
    Run a command with Popen and return the results or print the errors
    '''
    ###
    show_messages()
    dprint("[ Deviot {0} ] Starting...\n", True, '2.0.0')
    ###

    if(not cwd):
        cwd = os.getcwd()

    command = prepare_command(command)
    process = subprocess.Popen(command, stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, cwd=cwd,
                               universal_newlines=True, shell=True)

    if(realtime):
        while True:
            output = process.stdout.readline()
            # exit when there is nothing to show
            if output == '' and process.poll() is not None:
                break

            if output:
                dprint(output)

    # return code and stdout
    output = process.communicate()
    stdout = output[0]
    return_code = process.returncode

    dstop()

    if stdout and set_return:
        return stdout
    
    return (return_code, stdout)


def prepare_command(post_command, verbose=False):

    cmd = " ".join(post_command)
    command = tools.create_command(['pio', '-f', '-c', 'sublimetext'])
    command.extend(post_command)

    # verbose mode
    if(verbose and 'run' in cmd and '-e' in cmd and 'upload' not in cmd):
        command.extend(['-vvv'])

    command.append("2>&1")
    command = ' '.join(command)

    return command
"""
def show_messages():
    """Show message in deviot console
    
    Using the MessageQueue package, this function
    start the message printer queue. (call it from the begining)
    
    global variables

    dprint overrides `message.put()` instead calling it that way, 
    dprint() will make the same behavior

    derror will print the message in the console but will stop the
    execution of the code

    dstop is the reference of the stop_print method in the MessageQueue
    class, it will called when derror is executed
    """
    from ..libraries.messages import MessageQueue

    global dprint
    global derror
    global dstop

    message = MessageQueue()
    message.start_print()
    dprint = message.put
    derror = show_error
    dstop = message.stop_print

def show_error(text, *args):
    """Show Error
    
    When it's called print the error in the console but stop the
    execution of the program after doing it

    Use this function calling derror()
    
    Arguments:
        text {str} -- message to show in the console
        *args {str} -- strings to be replaced with format()
    """
    dprint(text, False, *args)
    dstop()
    exit(0)
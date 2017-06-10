# !/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess
from sys import exit

from ..libraries import tools


def run_command(command, cwd=None, realtime=False, set_return=None):
    '''
    Run a command with Popen and return the results or print the errors
    '''
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
                print(output)

    # return code and stdout
    output = process.communicate()
    stdout = output[0]
    return_code = process.returncode

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

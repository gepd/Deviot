#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import subprocess
import os
import re
import time
import sublime

try:
    from . import Messages
    from .Preferences import Preferences
    from .I18n import I18n
except:
    from Libs import Messages
    from Libs.Preferences import Preferences
    from libs.I18n import I18n

_ = I18n().translate


class CommandsPy(object):
    """
    Class to handle the different functions allowed by
    the platformio API, to know more information visit
    the web site: www.platformio.org
    """

    def __init__(self, env_path=False, console=False, cwd=None):
        super(CommandsPy, self).__init__()
        self.Preferences = Preferences()
        self.message_queue = Messages.MessageQueue(console)
        self.message_queue.startPrint()
        self.error_running = False
        self.console = console
        self.cwd = cwd

        # env_path from preferences
        if(not env_path):
            env_path = self.Preferences.get('env_path', False)

        # Set the enviroment Path
        if(env_path):
            os.environ['PATH'] = env_path

    def runCommand(self, commands, setReturn=False, extra_message=None):
        """
        Runs a CLI command to  do/get the differents options from platformIO
        """

        if(not commands):
            return False

        # get verbose from preferences
        verbose = self.Preferences.get('verbose_output', False)

        # get command
        self.type_build = False
        command = self.createCommand(commands, verbose)

        # Console message
        cmd_type = self.getTypeAction(command)
        current_time = time.strftime('%H:%M:%S')
        start_time = time.time()
        if(cmd_type):
            self.message_queue.put(cmd_type, current_time, extra_message)

        # run command
        process = subprocess.Popen(command, stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, cwd=self.cwd,
                                   universal_newlines=True, shell=True)

        show_warning = False
        show_error = False
        # real time
        if(not verbose and 'version' not in command and
                'json' not in command and
                'upload' not in command):
            error, down, previous = False, False, ''
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    # print took time and break the loop
                    if(error):
                        self.error_running = True
                    break

                if('warning:' in output.lower() or
                   'in function' in output.lower() or
                   'in file' in output.lower() or
                   'error:' in output.lower() or
                   '^' in output):
                    if('^' in output):
                        output = previous + output
                    self.message_queue.put(output)

                if('warning:' in output.lower()):
                    show_warning = True
                if('error:' in output.lower()):
                    show_error = True

                if(output.strip()):
                    previous = output

                # realtime output for build command
                if('run' in command and '-e' in command and not 'upload'):
                    if('installing' in output.lower()):
                        package = re.match(
                            r'\w+\s(\w+-*\w+)\s\w+', output).group(1)
                        self.message_queue.put('install_package_{0}', package)

                if('already' in output.lower()):
                    self.message_queue.put('already_installed')

                if('downloading' in output.lower() and
                        output.replace(" ", "") and
                        output.replace(" ", "") != previous):

                    message = 'downloading_package'
                    if(down and 'lib' in command and 'install' in command):
                        message = 'download_dependece'
                    self.message_queue.put(message)
                    down = True

                if('unpacking' in output.lower() and
                        output.replace(" ", "") and
                        output.replace(" ", "") != previous):
                    self.message_queue.put('unpacking')

                if(output.replace(" ", "")):
                    previous = output

        # output
        output = process.communicate()
        stdout = output[0]
        stderr = output[1]
        return_code = process.returncode

        # set error
        if(return_code > 0):
            self.error_running = True

        current_time = time.strftime('%H:%M:%S')
        diff_time = time.time() - start_time
        diff_time = '{0:.2f}'.format(diff_time)
        self.status_bar = ""

        # Print success status
        if(self.console and not verbose and
                return_code == 0 and not show_warning):
            if(self.type_build):
                message = 'success_took_{0}{1}'
            else:
                message = 'success_took_{1}'
            self.status_bar = _('success')
            self.message_queue.put(message, current_time, diff_time)

        # output warning
        if(show_warning and not show_error):
            self.status_bar = _('success_warnings')
            message = 'success_warnings_took__{0}{1}'
            self.message_queue.put(message, current_time, diff_time)

        # output error
        if(show_error):
            self.status_bar = _('error')
            message = 'error_took_{0}{1}'
            self.message_queue.put(message, current_time, diff_time)

        # create window to show message in status bar
        if self.status_bar:
            self.status_erase_time = 5000
            sublime.set_timeout(self.setStatus, 0)

        # print full verbose output (when is active)
        if(verbose):
            self.message_queue.put(stdout)
            if(stderr):
                self.message_queue.put(stderr)

        # return output
        if(setReturn):
            return stdout

    def getTypeAction(self, command):
        """
        Get the type of action, to get the header
        and print it in the user console

        Arguments:
            command {string} -- CLI command
        """
        if 'init' in command:
            return 'init_project_{0}'
        elif '-e' in command and 'upload' not in command:
            self.type_build = True
            return 'built_project_{0}'
        elif '--upload-port' in command:
            return 'uploading_firmware_{0}'
        elif '-t clean' in command:
            return 'clean_built_files__{0}'
        elif 'lib install' in command:
            return'installing_lib_{0}{1}'
        elif 'lib uninstall' in command:
            return'uninstalling_lib_{0}{1}'
        else:
            return None

    def createCommand(self, commands, verbose):
        """
        Create the full CLI command based in the verbose mode

        Arguments:
            command {list} -- actions command to run in platformIO
            verbose {bool} -- verbose mode user preference
        """
        options = commands[0]

        try:
            args = " ".join(commands[1:])
        except:
            args = ''

        # output errors only
        if(not verbose and 'run' in options and
                '-e' in args and 'upload' not in args):
            args += ' -v --verbose'

        command = "platformio -f -c sublimetext %s %s 2>&1" % (
            options, args)

        return command

    def setStatus(self):
        window = sublime.active_window()
        view = window.active_view()

        view.run_command(
            'add_status', {'text': self.status_bar,
                           'erase_time': self.status_erase_time})

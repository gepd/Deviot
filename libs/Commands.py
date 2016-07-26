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

from . import Messages
from .Preferences import Preferences
from .I18n import I18n
from .Paths import getEnvBinDir

_ = I18n().translate


class CommandsPy(object):
    """
    Class to handle the different functions allowed by
    the platformio API, to know more information visit
    the web site: www.platformio.org
    """

    def __init__(self, console=False, env_path=False, cwd=None):
        super(CommandsPy, self).__init__()
        env_bin_dir = getEnvBinDir()
        self.python = os.path.join(env_bin_dir, 'python')
        self.Preferences = Preferences()
        self.error_running = False
        self.console = console
        self.cwd = cwd

        # not use env vars in osx
        if(sublime.platform() == 'osx'):
            return

        # env_path from preferences
        if(not env_path):
            env_path = self.Preferences.get('env_path', False)

        # Set the enviroment Path
        if(env_path):
            os.environ['PATH'] = env_path

    def runCommand(self, commands, feedback=False, setReturn=False, extra_message=None, verbose=False):
        """Command

        Runs a CLI command to do/get the differents options from platformIO

        Arguments:
            commands {list} -- command to run

        Keyword Arguments:
            feedback {bool} -- if it's true shows the output in console (default: {False})
            setReturn {bool} -- if it's true return stdout (default: {False})
            extra_message {[str]} -- Push a text in the user console (default: {None})
            verbose {bool} -- When is true show full output in console (default: {False})

        Returns:
            str -- return the stdout of the command execution
        """
        real_time = True
        self.show_warning = False
        self.show_error = False
        self.previous = ''
        self.down_string = False
        self.verbose = verbose

        self.feedback = feedback
        if(feedback):
            self.message_queue = Messages.MessageQueue(self.console)
            self.message_queue.startPrint()

        if(not commands):
            return False

        # get verbose from preferences
        if(not self.verbose):
            self.verbose = self.Preferences.get('verbose_output', False)

        # get command
        self.type_build = False
        command = self.createCommand(commands)

        # time info
        current_time = time.strftime('%H:%M:%S')
        self.start_time = time.time()

        # Console message
        if(feedback):
            self.message_queue.put(feedback, current_time, extra_message)

        # run command
        process = subprocess.Popen(command, stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, cwd=self.cwd,
                                   universal_newlines=True, shell=True)

        if(setReturn):
            output = process.communicate()
            stdout = output[0]
            stderr = output[1]
            real_time = False

        if(real_time):
            # realtime output
            while True:
                output = process.stdout.readline()
                # exit when there is nothing to show
                if output == '' and process.poll() is not None:
                    break

                self.outputFilter(output, command)

                if(output.strip()):
                    self.previous = output.lower()

        # results
        return_code = process.returncode
        self.resultsOutput(return_code)
        # return output
        if(setReturn):
            if(return_code > 0):
                print(stderr)
            return stdout

    def createCommand(self, commands):
        """
        Create the full CLI command based in the verbose mode

        Arguments:
            command {list} -- actions command to run in platformIO
        """
        options = commands[0]

        try:
            args = " ".join(commands[1:])
        except:
            args = ' -v'

        # full verbose mode
        if(self.verbose and 'run' in options and '-e' in args and 'upload' not in args):
            args += ' -vvv'

        if(sublime.platform() == 'osx'):
            command = '"%s" -m platformio -f -c sublimetext %s %s 2>&1' % (
                self.python, options, args)
        else:
            command = "platformio -f -c sublimetext %s %s 2>&1" % (
                options, args)

        return command

    def outputFilter(self, output, command):
        """Filter

        catch the output of Popen in real time and filter it
        showing minimun information

        Arguments:
            output {[str]} -- text from Popen
            command {[str]} -- current command running
        """
        # show full output
        if(self.verbose):
            self.message_queue.put(output)
            return

        outputif = output.lower()

        # warning and errors
        if('warning:' in outputif and 'cygwin' not in outputif or
                'in function' in outputif or
                'reference' in outputif or 'in file' in outputif or
                'error:' in outputif or '^' in outputif):

            if('^' in outputif):
                output = self.previous + output
            self.message_queue.put(output)

        if('warning:' in outputif and 'cygwin' not in outputif):
            self.show_warning = True

        if('error:' in outputif):
            self.show_error = True

        if(': programmer' in outputif):
            output = re.sub(r"[^\: ][\w\s+]+$",
                            "El programador no responde", output)
            self.message_queue.put('\n' + output)

        if(' attempt ' in outputif):
            dic = {'attempt': 'intento',
                   'of': 'de',
                   'not in sync': 'no sincronizado'}
            output = multiwordReplace(output, dic)
            self.message_queue.put('\n' + output)

        if('[info]:' in outputif or '[error]:' in outputif):
            dic = {'Starting on': 'Iniciando en',
                   'Upload size': 'Tamaño de Carga',
                   'Sending invitation to': 'Enviando invitación a',
                   'Waiting for device': 'Esperando dispositivo',
                   'Waiting for result': 'Esperado resultado',
                   'Result': 'Resultado',
                   'Authentication': 'Autentificación',
                   'Failed': 'Fallida'}
            if("Starting" in output):
                output = '\n' + output
            output = multiwordReplace(output, dic)
            self.message_queue.put(output)

        # realtime output for build command
        if('run' in command and '-e' in command and not 'upload'):
            if('installing' in outputif):
                package = re.match(r"\w+ (\w+\W?\w+?)\s", output).group(1)
                self.message_queue.put('install_package_{0}', package)

        if('already' in outputif):
            package = re.match(r"\w+ (\w+\W?\w+?)\s", self.previous).group(1)
            self.message_queue.put('already_installed{0}', package)

        if('downloading' in outputif.strip() and outputif != self.previous):
            message = 'downloading_package{0}' if 'lib' not in command else 'download_lib'
            package = re.match(r"\w+ (\w+\W?\w+?)\s", self.previous).group(1)

            if(self.down_string and 'lib' in command and 'install' in command):
                message = 'download_dependece'
            self.message_queue.put(message, package)
            self.down_string = True

        if('unpacking' in outputif and outputif.replace(" ", "") and
                outputif.replace(" ", "") != self.previous):
            self.message_queue.put('unpacking')

    def resultsOutput(self, return_code):
        """Results

        Shows information with the result of processing the file. If the
        verbose mode is true the output is shown as it (not filtered)

        Arguments:
            return_code {[int]} -- 0 if wasn't an error 1 if there was an error
        """
        # set error
        if(return_code > 0):
            self.error_running = True

        current_time = time.strftime('%H:%M:%S')
        diff_time = time.time() - self.start_time
        diff_time = '{0:.2f}'.format(diff_time)
        self.status_bar = ""

        # Print success status
        if(self.feedback and not self.verbose and
                return_code == 0 and not self.show_warning):
            if(self.type_build):
                message = 'success_took_{0}{1}'
            else:
                message = 'success_took_{1}'
            self.status_bar = _('success')
            self.message_queue.put(message, current_time, diff_time)

        # output warning
        if(self.show_warning and not self.show_error):
            self.status_bar = _('success_warnings')
            message = 'success_warnings_took__{0}{1}'
            self.message_queue.put(message, current_time, diff_time)

        # output error
        if(self.show_error or self.error_running):
            self.status_bar = _('error')
            message = 'error_took_{0}{1}'
            self.message_queue.put(message, current_time, diff_time)

        # create window to show message in status bar
        if self.status_bar:
            self.status_erase_time = 5000
            sublime.set_timeout(self.setStatus, 0)

    def setStatus(self):
        """Status Bar

        Display the result of the process in the status bar
        """
        window = sublime.active_window()
        view = window.active_view()

        view.run_command(
            'add_status', {'text': self.status_bar,
                           'erase_time': self.status_erase_time})


def multiwordReplace(text, wordDic):
    """
    take a text and replace words that match a key in a dictionary with
    the associated value, return the changed text
    """
    rc = re.compile('|'.join(map(re.escape, wordDic)))

    def translate(match):
        return wordDic[match.group(0)]
    return rc.sub(translate, text)

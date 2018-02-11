# This file is part of the uPiot project, https://github.com/gepd/upiot/
#
# MIT License
#
# Copyright (c) 2017 GEPD
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import time
import threading
import sublime

from re import findall
from sys import platform
from subprocess import Popen, PIPE
from functools import partial
from collections import deque

from ..libraries import messages
from ..libraries.tools import prepare_command, get_setting
from ..libraries.thread_progress import ThreadProgress
from .project_recognition import ProjectRecognition

_COMMAND_QUEUE = deque()
_BUSY = False


class AsyncProcess(object):

    def __init__(self, cmd, listener):
        self.listener = listener
        self.killed = False
        self.start_time = time.time()

        self.proc = Popen(
            cmd,
            stdout=PIPE,
            stderr=PIPE,
            stdin=PIPE,
            shell=True)

        if(self.proc.stdout):
            th1 = threading.Thread(target=self.read_stdout)
            th1.start()
            th1.join()
            ThreadProgress(th, '', '')

        if(self.proc.stderr):
            th2 = threading.Thread(target=self.read_stderr)
            th2.start()
            th2.join()

    def kill(self):
        """Kill process

        kill the encapsulated subprocess.Popen
        """
        if(not self.killed):
            self.killed = True
            if(platform == 'win32'):
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                subprocess.Popen("taskkill /PID " + str(self.proc.pid),
                                 startupinfo=startupinfo)
            else:
                self.proc.terminate()
            self.listener = None

    def poll(self):
        return self.proc.poll() is None

    def exit_code(self):
        """
        return the exit code
        """
        return self.proc.poll()

    def read_stdout(self):
        """Read stdout output

        Reads the stdout outputs when the data is available
        and send it to the listener to be printed
        """
        while True:
            data = os.read(self.proc.stdout.fileno(), 2 ** 15)

            if(len(data) > 0):
                if(self.listener):
                    self.listener._on_data(data)
            else:
                self.proc.stdout.close()
                if(self.listener):
                    self.listener._on_finished(self)
                break

    def read_stderr(self):
        """Read stderr output

        Reads the stderr outputs when the data is available
        and send it to the listener to be printed
        """
        while True:
            data = os.read(self.proc.stderr.fileno(), 2 ** 15)

            if len(data) > 0:
                if self.listener:
                    self.listener._on_data(data)
            else:
                self.proc.stderr.close()
                break


class Command(ProjectRecognition):
    _txt = None
    _exit_code = None

    def init(self, extra_name=None, messages=None):
        self.extra_name = extra_name
        self._txt = messages

    def run_command(self, cmd, kill=False, word_wrap=True, in_file=False):
        self.window = sublime.active_window()
        self._exit_code = None

        global _COMMAND_QUEUE
        global _BUSY

        # kill the process
        if(kill):
            if(self.proc):
                self.proc.kill()
                self.proc = None
            return

        if(_BUSY):
            _COMMAND_QUEUE.append(cmd)
            return

        if(not self._txt):
            try:
                self._txt = messages.Messages(self.extra_name)
                self._txt.create_panel(in_file=in_file)
            except:
                pass

        self.encoding = 'utf-8'
        self.proc = None

        verbose = get_setting('verbose_output', False)
        cmd = prepare_command(cmd, verbose)

        if(self.cwd):
            os.chdir(self.cwd)

        try:
            _BUSY = True
            self.proc = AsyncProcess(cmd, self)
        except Exception as e:
            pass

    def exit_code(self):
        return self._exit_code

    def _on_data(self, data):
        try:
            characters = data.decode(self.encoding)
        except:
            characters = "[Decode error - output not " + self.encoding + "]\n"

        # Normalize newlines, Sublime Text always uses a single \n separator
        # in memory.
        characters = characters.replace('\r\n', '\n').replace('\r', '\n')
        self._txt.print(characters)

    def _finish(self, proc):
        elapsed = time.time() - proc.start_time
        exit_code = proc.exit_code()
        self._exit_code = exit_code

        if(exit_code == 0 and not len(_COMMAND_QUEUE)):
            sublime.status_message("Build finished")
        else:
            sublime.status_message("Build finished with errors")

        # run next command in the deque
        run_next()

    def _on_finished(self, proc):
        sublime.set_timeout(partial(self._finish, proc), 0)


def run_next():
    global _COMMAND_QUEUE
    global _BUSY

    _BUSY = False

    if(len(_COMMAND_QUEUE)):
        Command().run_command(_COMMAND_QUEUE.popleft())
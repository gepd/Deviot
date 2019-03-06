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
import html
import threading
import sublime

from re import findall, search
from sys import platform
from subprocess import Popen, PIPE
from functools import partial
from collections import deque

from ..libraries import messages
from ..libraries.tools import prepare_command, get_setting, get_sysetting
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
            ThreadProgress(th1, '', '')

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
                    time.sleep(0.01)
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

    show_errors_inline = None
    errs_by_file = {}
    phantom_sets_by_buffer = {}

    def __init__(self):
        super(Command, self).__init__()
        self._output = None

    def init(self, extra_name=None, messages=None):
        self._extra_name = extra_name
        self._txt = messages

    def run_command(self, cmd, kill=False, word_wrap=True, in_file=False):
        self.errs_by_file = {}
        self.window = sublime.active_window()

        # sets environment
        env_path = get_sysetting('env_path', False)
        if(env_path):
            os.environ['PATH'] = env_path

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
                self._txt = messages.Messages(self._extra_name)
                self._txt.create_panel(in_file=in_file)
            except:
                pass

        self.encoding = 'utf-8'
        self.proc = None
        self.show_errors_inline = get_setting('show_errors_inline', True)

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
        return self.proc.exit_code()

    def get_output(self):
        return self._output

    def _on_data(self, data):
        try:
            characters = data.decode(self.encoding)
        except:
            characters = "[Decode error - output not " + self.encoding + "]\n"

        # if there is not printer, store the data
        if(not self._txt):
            if(not self._output):
                self._output = characters
            else:
                self._output += characters
            return

        # Normalize newlines, Sublime Text always uses a single \n separator
        # in memory.
        characters = characters.replace('\r\n', '\n').replace('\r', '\n')
        self._txt.print(characters)

        if(self.show_errors_inline):
            # errors inline
            errors = self.find_all_pio_errors(characters)
            for file, line, column, text in errors:
                if file not in self.errs_by_file:
                    self.errs_by_file[file] = []
                self.errs_by_file[file].append((line, column, text))

            self.update_phantoms()

    def _finish(self, proc):
        exit_code = proc.exit_code()

        if(exit_code == 0 and not len(_COMMAND_QUEUE)):
            sublime.status_message("Build finished")
        else:
            sublime.status_message("Build finished with errors")

        if(self._txt):
            end_time = time.strftime('%c')
            self._txt.print("\n[{0}]", end_time)

        # run next command in the deque
        run_next()

    def _on_finished(self, proc):
        sublime.set_timeout(partial(self._finish, proc), 0)

    def find_all_pio_errors(self, text):
        """Find PlatformIO errors

        Extract all errors gived by PlatformIO

        Arguments:
            text {str} -- line string with error

        Returns:
            [tuple] -- (file_path, line_number, colum_number, error_text)
        """
        error = []

        # substract error with regex
        if('error:' in text):
            result = search('(.+):([0-9]+):([0-9]+):\s(.+)', text)
            if(result is not None):
                file_path = result.group(1)
                line_number = result.group(2)
                column_number = result.group(3)
                error_txt = result.group(4)

                error.append(
                    [
                        file_path,
                        int(line_number),
                        int(column_number),
                        error_txt
                    ]
                )

        return error

    def update_phantoms(self):
        stylesheet = '''
            <style>
                div.content {
                    padding: 0.45rem 0.45rem 0.45rem 0.45rem;
                    margin: 0.2rem 0;
                    border-radius: 4px;
                }
                div.content span.message {
                    color: white;
                    padding-right: 0.4rem;
                    padding-left: 0.5rem;
                }
                span.error_box {
                    padding: 5px;
                    color: white;
                    font-weight: bold;
                    border-radius: 3px;
                    background-color: red;
                }
                span.warning_box {
                    padding: 5px;
                    color: white;
                    font-weight: bold;
                    border-radius: 3px;
                    background-color: #d1cd00;
                }
                div.content a {
                    text-decoration: inherit;
                    padding: 0.35rem 0.7rem 0.45rem 0.8rem;
                    position: relative;
                    bottom: 0.05rem;
                    border-radius: 4px;
                    font-weight: bold;
                }
                html.dark div.content a {
                    background-color: #00000018;
                }
                html.light div.content a {
                    background-color: #ffffff18;
                }
            </style>
        '''

        for file, errs in self.errs_by_file.items():
            view = self.window.find_open_file(file)
            if view:

                buffer_id = view.buffer_id()
                if buffer_id not in self.phantom_sets_by_buffer:
                    phantom_set = sublime.PhantomSet(view, "exec")
                    self.phantom_sets_by_buffer[buffer_id] = phantom_set
                else:
                    phantom_set = self.phantom_sets_by_buffer[buffer_id]

                phantoms = []

                for line, column, text in errs:
                    pt = view.text_point(line - 1, column - 1)
                    phantoms.append(sublime.Phantom(
                        sublime.Region(pt, view.line(pt).b),
                        ('<body id=inline-error>' + stylesheet +
                            '<div class="content">'
                            '<span class="error_box">error</span>' +
                            '<span class="message">' + html.escape(text, quote=False) + '</span>' +
                            '<a href=hide>' + chr(0x00D7) + '</a></div>' +
                            '</div></body>'),
                        sublime.LAYOUT_BELOW,
                        on_navigate=self.on_phantom_navigate))

                phantom_set.update(phantoms)

    def hide_phantoms(self):
        for file, errs in self.errs_by_file.items():
            view = self.window.find_open_file(file)
            if view:
                view.erase_phantoms("exec")

        self.errs_by_file = {}
        self.phantom_sets_by_buffer = {}
        self.show_errors_inline = False

    def on_phantom_navigate(self, url):
        self.hide_phantoms()


def run_next():
    global _COMMAND_QUEUE
    global _BUSY

    _BUSY = False

    if(len(_COMMAND_QUEUE)):
        Command().run_command(_COMMAND_QUEUE.popleft())

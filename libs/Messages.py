#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import threading
import sublime
import time

try:
    from . import Tools
except:
    from libs import Tools

python_version = Tools.getPythonVersion()

if python_version < 3:
    import Queue as queue
else:
    import queue


class MessageQueue(object):
    """Message Queue

    Print messages in the user console,
    placed in the message queue
    """

    def __init__(self, console=None):
        self.queue = queue.Queue(0)
        self.is_alive = False
        self.console = console

    def put(self, text, *args):
        if text.endswith('\\n'):
            text = text[:-2] + '\n'
        self.queue.put(text)

    def startPrint(self, one_time=False):
        if not self.is_alive:
            self.is_alive = True
            thread = threading.Thread(
                target=lambda: self.printScreen(one_time))
            thread.start()

    def printScreen(self, one_time=False):
        if one_time:
            self.printOnce()
        else:
            while self.is_alive:
                self.printOnce()
                time.sleep(0.01)

    def printOnce(self):
        while not self.queue.empty():
            text = self.queue.get()
            print(text)
            if self.console:
                self.console.printScreen(text)
            else:
                print(text)
            time.sleep(0.01)

    def stopPrint(self):
        while(not self.queue.empty()):
            time.sleep(2)
        self.is_alive = False


class Console:
    """User Console

    Creates the user console to show different messages.
    """

    def __init__(self, window, name='deviot_console'):
        self.name = name
        self.window = window

        if python_version < 3:
            self.panel = self.window.get_output_panel(self.name)
        else:
            self.panel = self.window.create_output_panel(self.name)

        self.panel.set_name(self.name)

    def printScreen(self, text):
        sublime.set_timeout(lambda: self.println(text), 0)

    def println(self, text):
        if(len(text)):
            panel_name = 'output.' + self.name
            self.window.run_command("show_panel", {"panel": panel_name})
            self.panel.set_read_only(False)
            if(python_version < 3):
                edit = self.panel.begin_edit()
                self.panel.insert(edit, self.panel.size(), text)
                self.panel.end_edit(edit)
            else:
                self.panel.run_command("append", {"characters": text})
            self.panel.set_read_only(True)

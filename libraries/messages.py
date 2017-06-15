#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sublime
from time import strftime
from sys import exit
from queue import Queue
from threading import Thread
from time import sleep
from sys import exit

from .I18n import I18n

class Console(object):
    """Deviot Console
    
    Shows the message int he deiot console, it's use with
    message queue
    """
    def __init__(self):
        self.window = sublime.active_window()

        self.panel = self.window.create_output_panel('exec')
        self.panel.set_syntax_file("Packages/Text/Plain text.tmLanguage")
        self.panel.set_name('exec')

    def print_screen(self, text):
        view = self.window.find_output_panel('exec')

        if(view.size() < 1):
            self.window.run_command("show_panel", {"panel": "output.exec"})

        self.panel.set_read_only(False)
        self.panel.run_command("append", {"characters": text})
        self.panel.run_command("move_to", {"extend": False, "to": "eof"})
        self.panel.set_read_only(True)

class MessageQueue(object):
    """Message Queue

    Handles the queue to print messages in the console. To use it
    Create a new instance and call start_print, add message to the
    queue with put. stop_print will stop to search new messages.

    message = MessageQueue()
    message.start_print()
    message.put("message")
    message.stop_print()

    start_print() and stop_print() are executed in a new thred to avoid
    block the sublime text UI
    """

    def __init__(self, start_header=None, *args):
        super(MessageQueue, self).__init__()
        self.queue = Queue(0)
        self.console = Console().print_screen
        self.is_alive = False
        self.is_first = True
        self.stopping = False
        self.start_header = start_header
        self.header_args = args

    def set_console(self, console):
        self.console = console

    def put(self, text, hide_hour=False, *args):
        """Put new message
        
        Puts a new message in the queue
        
        Arguments:
            text {str} -- message to be displayed
            *args {str} -- string to be replaced with format()
        
        Keyword Arguments:
            hide_hour {bool} -- avoid to add the hour in the
                                message (default: {False})
        """ 
        text = I18n().translate(text, *args)
        
        if '\\n' in text:
            text = text.replace('\\n', '\n')

        empty = False
        if(not text.strip()):
            empty = True

        if(not hide_hour):
            text = self.add_hour(text)

        if(not empty):
            self.queue.put(text)

    def start_print(self):
        """Start Print
        
        Starts a new thread to wait the messages to be shown
        in the console
        """
        if(not self.is_alive):
            self.is_alive = True

            if(self.start_header and self.is_first):
                self.put(self.start_header, True, *self.header_args)
                self.is_first = False
            
            thread = Thread(target=lambda: self.print())
            thread.start()

    def print(self):
        """Print
        
        Here is where the magic happens
        """
        while(self.is_alive):
            while(not self.queue.empty()):
                text = self.queue.get()
                self.console(text)
                sleep(0.01)
            sleep(0.01)


    def stop_print(self):
        """Stop queue
        
        Start a new thread to stop the queue, if there is any message
        in the queue, it will wait until it's empty
        """
        if(not self.stopping):
            self.stopping = True
            thread = Thread(target=lambda: self.stop())
            thread.start()
    
    def stop(self):
        """Stop
        
        Here is where the magic happens
        """
        while(not self.queue.empty()):
            sleep(0.05)
        self.is_alive = False
        self.stopping = False

    def print_once(self, text, *args):
        if(self.is_alive):
            self.put(text, False, *args)
            self.stop_print()

    def add_hour(self, txt):
        """Format arguments
        
        Adds the current time (HH:MM:SS) to the given string
        
        Arguments:
            txt {str} -- message string
        
        Returns:
            [str] -- final string with time + message
        """
        time = strftime('%H:%M:%S')
        txt = time + ' ' + txt

        return txt
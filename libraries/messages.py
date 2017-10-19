#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sublime
import html
from os import path
from re import search
from time import strftime
from sys import exit
from queue import Queue
from threading import Thread
from time import sleep
from sys import exit
from .I18n import I18n
from .tools import findInOpendView, get_setting
from .paths import getPluginName

errs_by_file = {}
phantom_sets_by_buffer = {}
first_scroll = False

class Console(object):
    """Deviot Console
    
    Shows the message int he deiot console, it's use with
    message queue
    """

    def __init__(self):
        self.window = sublime.active_window()
        self.view = self.window.active_view()
        self.file_name = self.view.file_name()
        self.panel = None
        self.name = None

    def print_screen(self, text):
        size = self.panel.size()
        auto_clean = get_setting('auto_clean', True)

        sel = self.panel.sel()[0]
        line_end = self.panel.rowcol(sel.end())[0] + 2

        if(auto_clean and line_end > 30000):
            self.clean_console()

        if(size < 1 and self.name == 'exec'):
            self.window.run_command("show_panel", {"panel": "output.exec"})

        self.panel.set_read_only(False)
        self.panel.run_command("append", {"characters": text})
        self.panel.set_read_only(True)

        automatic_scroll = get_setting('automatic_scroll', True)
        if(automatic_scroll or self.name == 'exec'):
            self.panel.run_command("move_to", {"extend": False, "to": "eof"})

    def set_console(self, name='exec'):
        self.name = name
        self.window, self.panel = findInOpendView(name)

        if(not self.panel):
            if(name == 'exec' or name == 'sexec'):
                self.panel = self.window.create_output_panel('exec')
                self.panel.set_name('exec')

                if(name == 'exec'):
                    package_name = getPluginName()
                    syntax = "Packages/{0}/Console.tmLanguage".format(package_name)
                    self.panel.assign_syntax(syntax)
                else:
                    self.panel.assign_syntax("Packages/Text/Plain text.tmLanguage")
            else:
                self.open_panel()

    def clean_console(self):
        self.window.focus_view(self.panel)
        self.panel.set_read_only(False)
        self.window.run_command("deviot_clean_view")
        self.panel.set_read_only(True)

    def open_panel(self, direction=False):
        
        if(direction):
            options = {'direction': 'down', 'give_focus': True}
            self.window.run_command('deviot_create_pane', options)

        self.panel = self.window.new_file()
        self.panel.set_name(self.name)

        self.panel.run_command('toggle_setting', {'setting': 'word_wrap'})
        self.panel.set_scratch(True)
        self.window.focus_view(self.panel)

class MessageQueue(Console):
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
        self.is_alive = False
        self.is_first = True
        self.stopping = False
        self.start_header = start_header
        self.header_args = args

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
        if(not text):
            return
    
        text = I18n().translate(text, *args)
        
        if('\\n' in text[-2:]):
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
        self.hide_phantoms()
        
        if(not self.panel):
            self.set_console()

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
                
                if(': error:' in text or ': fatal error:' in text):
                    self.service_text_queue(text)
                self.print_screen(text)
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
        """Print one time
        
        Print a message one time and stop the queue
        
        Arguments:
            text {str} -- text to display
            *args {str} -- text to replace in the 'text' var
        """
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

    def service_text_queue(self, text):
        """error data
        
        search the data of the error: file affected, column, line
        and error text and store it in the global var errs_by_file
        
        Arguments:
            text {str} -- line with the error
        """
        global errs_by_file
        
        result = search("(.+):([0-9]+):([0-9]+):\s(.+)", text)

        if(not result):
            return

        file = self.file_name
        file_in_line = path.normpath(result.group(1))
        line = result.group(2)
        column = result.group(3)
        txt = result.group(4)
        m_type = None

        if('error' in txt):
            txt = txt.replace('error: ', '')
            m_type = 'error'
        elif('warning' in txt):
            txt = txt.replace('warning: ', '')
            m_type = 'warning'

        if(file not in errs_by_file):
            errs_by_file[file] = []

        errs_by_file[file].append((int(line) -1, int(column), m_type, txt))
        self.update_phantoms()

    def update_phantoms(self):
        """show phantom

        Show the error in the phantom
        """
        global first_scroll

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

        for file, errs in errs_by_file.items():
            view = self.window.find_open_file(file)
            if view:
                buffer_id = view.buffer_id()
                if buffer_id not in phantom_sets_by_buffer:
                    phantom_set = sublime.PhantomSet(view, "exec")
                    phantom_sets_by_buffer[buffer_id] = phantom_set
                else:
                    phantom_set = phantom_sets_by_buffer[buffer_id]

                phantoms = []

                for line, column, m_type, text in errs:
                    pt = view.text_point(line - 1, column - 1)
                    phantoms.append(sublime.Phantom(
                        sublime.Region(pt, view.line(pt).b),
                        ('<body id=inline-error>' + stylesheet + \
                            '<div class="content">' + \
                            '<span class="' + m_type + '_box">' + m_type + '</span>' + \
                            '<span class="message">' + text + '</span>' + \
                            '<a href=hide>' + chr(0x00D7) + '</a>' + \
                            '</div></body>'),
                        sublime.LAYOUT_BELOW,
                        on_navigate=self.on_phantom_navigate))

                    if(not first_scroll):
                        view.sel().clear()
                        view.sel().add(sublime.Region(pt))
                        view.show(pt)
                        first_scroll = True

                phantom_set.update(phantoms)

    def hide_phantoms(self):
        """hide phantom
        
        erase the phantom from the view
        """
        global errs_by_file
        global phantom_sets_by_buffer
        global first_scroll

        for file, errs in errs_by_file.items():
            view = self.window.find_open_file(file)
            if view:
                view.erase_phantoms("exec")

        errs_by_file = {}
        phantom_sets_by_buffer = {}
        first_scroll = False

    def on_phantom_navigate(self, url):
        """on close
        
        Hide the phantom when the "x" is pressed
        
        Arguments:
            url {str} -- attribute of the link clicked.
        """
        self.hide_phantoms()
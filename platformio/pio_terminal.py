# !/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sublime
import sublime_plugin
from threading import Thread

from ..libraries import tools, paths
from .run_command import run_command
from ..libraries.message import MessageQueue


class PioTerminal(object):

    def __init__(self):
        self.name = 'PlatformIO Terminal'
        self.window, self.view = tools.findInOpendView(self.name)
        self.Msg = MessageQueue(self.write_in_terminal)

    def open_terminal(self):
        """
        opens a new window, always in a new group at the bottom, and allows
        to process platformio commands
        """
        if self.view is None:
            options = {'direction': 'down', 'give_focus': True}
            self.window.run_command('create_pane', options)

            self.view = self.window.new_file()
            self.view.set_name(self.name)

            self.view.run_command('toggle_setting', {'setting': 'word_wrap'})
            self.view.set_scratch(True)
            self.window.focus_view(self.view)

        self.show_input()

    def close_terminal(self):
        """
        Close the PlatformIO console including the bottom panel
        """
        if self.view is not None:
            self.window.focus_view(self.view)
            self.window.run_command("close")
            self.window.run_command('destroy_pane', {'direction': 'self'})

    def show_input(self):
        """
        shows an input to run the commdns
        """
        cap = ' # '
        self.window.show_input_panel(cap, '', self.send_cmd_thread, None, None)

    def write_in_terminal(self, text):
        """
        sends a text to the console and adds a new line at te end
        """

        self.window.focus_view(self.view)
        self.view.set_read_only(False)
        self.view.run_command("append", {"characters": text})
        self.view.set_read_only(True)
        self.view.run_command("move_to", {"extend": False, "to": "eof"})

    def send_cmd(self, cmd):
        """
        process the given command in a new thread
        """
        if(not cmd):
            return

        # start message queue
        self.Msg.start_print()

        # header
        self.write_in_terminal("\nCommand: %s\n" % cmd)
        self.write_in_terminal("==========================\n")

        # check if the command isn't pio type an try to execute it
        if(self.terminal_extra_commands(cmd)):
            self.show_input()
            return

        if('pio' not in cmd):
            self.write_in_terminal("command invalid (try: help)\n")
            return

        # INPROVE THIS #
        cmd = cmd.replace('pio ', '').replace('platformio ', '')
        cmd = cmd.split(" ")

        # run command in a new Thread
        thread = Thread(target=run_command(cmd, callback=self.Msg.put))
        thread.start()

        self.Msg.stop_print()
        self.show_input()

    def send_cmd_thread(self, cmd):
        """
        runs the 'send_cmd' method in a new thread to avoid crashes
        and performance problems
        """
        thread = Thread(target=self.send_cmd, args=(cmd,))
        thread.start()

    def terminal_extra_commands(self, cmd):
        """
        All extra commands to execute in the terminal
        """

        if(len(cmd.split(" ")) > 1):
            cmd = cmd.split(" ")

        options = {
            'help': self.help_terminal,
            'clear': self.clean_terminal,
            'cwd': self.show_cwd,
            'cd': self.set_cwd,
            'ls': self.list_cwd,
            'mk': self.mk_cwd,
            'rm': self.rm_cwd
        }

        try:
            args = " ".join(cmd[1:])
            options[cmd[0]](args)
            return True
        except:
            pass

        try:
            options[cmd]()
            return True
        except:
            pass

    def help_terminal(self):
        help_string = """cwd         Show the current working dir\n"""
        help_string += """cd          change directory\n"""
        help_string += """ls          list all files and folder in the cwd\n"""
        help_string += """mk          make the folder in the cwd\n"""
        help_string += """rm          remove the folder in the cwd\n"""
        help_string += """clear       clear all in the terminal window\n"""
        help_string += """pio --help  to see info about PlatformIO\n"""

        self.write_in_terminal(help_string)

    def clean_terminal(self):
        """
        Remove al text in the console
        """
        self.window.focus_view(self.view)
        self.view.set_read_only(False)
        self.window.run_command('clean_view')
        self.view.set_read_only(True)

    def show_cwd(self):
        cwd = os.getcwd()

        self.write_in_terminal(cwd + '\n')

    def set_cwd(self, path):
        cwd = os.getcwd()
        cwd = os.path.join(cwd, path)
        if(not os.path.isdir(cwd)):
            self.write_in_terminal('Not valid path\n')
            return
        os.chdir(path)
        cwd = os.getcwd()
        self.write_in_terminal(cwd + '\n')

    def list_cwd(self):
        from glob import glob
        cwd = os.getcwd()
        cwd = os.path.join(cwd, '*')
        for current in glob(cwd):
            self.write_in_terminal(current + '\n')

    def mk_cwd(self, path):
        cwd = os.getcwd()
        cwd = os.path.join(cwd, path)
        try:
            os.makedirs(path)
            self.write_in_terminal("Folder Created\n")
        except:
            self.write_in_terminal("Error creating folder\n")

    def rm_cwd(self, path):
        from shutil import rmtree
        cwd = os.getcwd()
        cwd = os.path.join(cwd, path)
        try:
            rmtree(cwd)
            self.write_in_terminal("Folder Removed\n")
        except:
            self.write_in_terminal("check the name of the folder\n")

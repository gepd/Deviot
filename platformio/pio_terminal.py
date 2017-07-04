# !/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sublime
import sublime_plugin
from threading import Thread
from time import sleep

from ..libraries import tools, paths
from ..libraries.messages import MessageQueue
from ..platformio.command import Command
from ..libraries.thread_progress import ThreadProgress
from ..libraries.I18n import I18n

class PioTerminal(Command):

    def __init__(self):
        super(PioTerminal, self).__init__()
        global _
        _ = I18n().translate

        name = 'PlatformIO Terminal'
        self.window, self.view = tools.findInOpendView(name)

        header = self.check_header()
        message = MessageQueue(header)
        message.set_console(name)
        message.start_print()
        
        self.dprint = message.put
        self.dstop = message.stop_print

    def check_header(self):
        """Terminal eader
        
        When the console is empty, it adds a string at the beginning
        
        Returns:
            str -- header string
        """
        header = None
        if(self.view is None or self.view.size() == 0):
            header = "pio_terminal"

        return header

    def close_terminal(self):
        """Close Terminal
        
        Close the PlatformIO console including the bottom panel
        """
        if self.view is not None:
            self.window.focus_view(self.view)
            self.window.run_command("close")
            self.window.run_command('destroy_pane', {'direction': 'self'})
            self.dstop()

    def print_screen(self, text):
        """Print on screen
        
        Print all the user interaction in the console (panel)

        Arguments:
            text {str} -- texto to append in the console
        """
        self.dprint(text)

    def show_input(self):
        """Show input
        
        Shows an input to run the commands
        """
        self.window.focus_view(self.view)
        cap = ' $ '
        self.window.show_input_panel(cap, '', self.nonblock_cmd, None, self.cancel_input)

    def nonblock_cmd(self, cmd):
        """New thread command
        
        Runs the 'send_cmd' method in a new thread to avoid crashes
        and performance problems
        
        Arguments:
            cmd {str} -- command to run
        """
        thread = Thread(target=self.send_cmd, args=(cmd,))
        thread.start()
        ThreadProgress(thread, _('processing'), '')

    def cancel_input(self):
        """Cancel queue
        
        Cancel the message queue when the input panel is cancel (esc key)
        """
        self.dstop()

    def send_cmd(self, cmd):
        """Process command
        
        Process the differents commands sended by the user. It first check if the command
        is a deviot command (remove, create folder, list directory etc). If the command start
        with 'pio' or 'platformio' executes the command otherwise display a "not found command"
        
        Arguments:
            cmd {str} -- command to execute
        """
        if(not cmd):
            self.dstop()
            return

        self.dprint("\n$ {0} \n".format(cmd), hide_hour=True)
        
        sleep(0.03)

        if(self.deviot_commands(cmd)):
            self.show_input()
            return

        cmd = cmd.replace('pio ', '').replace('platformio ', '')
        cmd = cmd.split(" ")

        self.cwd = os.getcwd()
        self.run_command(cmd)

        self.show_input()

    def deviot_commands(self, cmd):
        """Custom commands
        
        Custom commands to interact for the system, it includes
        create and remove a folder, list directories, clear console
        view, and other. Use the command help to see the complete list
        
        Arguments:
            cmd {str} -- command string
        
        Returns:
            bool -- True if was executed, false if the command wasn't recognised
        """
        cmd_return = True

        if(len(cmd.split(" ")) > 1):
            cmd = cmd.split(" ")
            args = " ".join(cmd[1:])

        if('help' == cmd):
            self.help_cmd()
        elif('clear' in cmd):
            self.clear_cmd()
        elif('cwd' in cmd):
            self.show_cwd()
        elif('cd' in cmd):
            self.set_cwd(cmd[1])
        elif('ls' in cmd):
            self.list_cwd()
        elif('mk' in cmd):
            self.mk_cwd(cmd[1])
        elif('rm' in cmd):
            self.rm_cwd(cmd[1])
        elif('pio' in cmd or 'platformio' in cmd):
            cmd_return = False
        else:
            self.dprint("invalid_command", hide_hour=True)
            self.show_input()

        return cmd_return


    def help_cmd(self):
        """List of cmomands
        
        Shows a list of all commands availables and the description of each one
        """
        from ..libraries.I18n import I18n

        width = 25

        cmd_string = ["cwd", "cd", "ls", "mk", "rm", "clear", "pio --help"]
        cmd_descript = ["cmd_cwd", "cmd_cd", "cmd_ls", "cmd_mk", "cmd_rm", "cmd_clear", "cmd_pio_help"]

        for cmd, description in zip(cmd_string, cmd_descript):
            description = I18n().translate(description)
            self.dprint("{}: {}\n".format(cmd.ljust(width), str(description).ljust(width)), hide_hour=True)

    def clear_cmd(self):
        """Clean view
        
        Cleans the console view
        """
        self.window.focus_view(self.view)
        self.view.set_read_only(False)
        self.window.run_command("deviot_clean_view")
        self.view.set_read_only(True)

        header = self.check_header()
        self.dprint(header, hide_hour=True)

    def show_cwd(self):
        """Currente directory
        
        Prints the current working directory
        """
        cwd = os.getcwd()
        self.dprint(cwd + '\n', hide_hour=True)

    def set_cwd(self, path):
        """Set directory
        
        Sets the current working directory. 
        
        Arguments:
            path {str} -- folder name (not full path)
        """
        cwd = os.getcwd()
        cwd = os.path.join(cwd, path)
        if(not os.path.isdir(cwd)):
            self.dprint('invalid_path', hide_hour=True)
            return
        os.chdir(path)
        cwd = os.getcwd()
        self.dprint(cwd + '\n', hide_hour=True)

    def list_cwd(self):
        """List of files and directories
        
        Shows the list of files and directories in the current working path
        """
        from glob import glob
        cwd = os.getcwd()
        cwd = os.path.join(cwd, '*')
        for current in glob(cwd):
            self.dprint(current + '\n', hide_hour=True)

    def mk_cwd(self, path):
        """Make folder
        
        Creates a new folder in the current working path
        
        Arguments:
            path {str} -- name of the folder to create (not full path)
        """
        cwd = os.getcwd()
        cwd = os.path.join(cwd, path)
        try:
            os.makedirs(path)
            self.dprint("created{0}", True, path)
        except:
            self.dprint("error_making_folder", hide_hour=True)

    def rm_cwd(self, path):
        """Remove folder
        
        Removes the folder in the current working path
        
        Arguments:
            path {str} -- folder name to remove (not full path)
        """
        from shutil import rmtree
        cwd = os.getcwd()
        cwd = os.path.join(cwd, path)
        try:
            rmtree(cwd)
            self.dprint("removed{0}", True, path)
        except:
            self.dprint("wrong_folder_name", hide_hour=True)

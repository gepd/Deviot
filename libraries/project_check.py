#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

from os import path

from ..platformio.project_recognition import ProjectRecognition
from .serial import serial_port_list
from .quick_menu import QuickMenu

class ProjectCheck(QuickMenu):
    """
    ProjectCheck handles the actions between sublime text and platformio.
    Before run a platformio command like initilize, compile or upload, this
    class check if the project meets the requirements to proceed with the
    command, for example if the current file has been saved, or if it's saved
    is in the src folder when the platformio sutrcture options is marked
    """
    def __init__(self):
        super(ProjectCheck, self).__init__()
        
        self.board_id = None
        self.port_id = None

    def is_iot(self):
        """IOT
        
        Checks if the file in the current view is in the list
        of the IOT types (accepted) or not
        
        Returns:
            bool -- true if is in the list false if not
        """
        ext = self.get_file_extension()
        accepted = ['ino', 'pde', 'cpp', 'c', '.S']

        if(ext not in accepted):
            return False
        return True

    def is_empty(self):
        """Empty File
        
        Checks if the file is empty or not
        
        Returns:
            bool -- true is if empty
        """
        size = self.view.size()

        if(size > 0):
            return False
        return True

    def is_unsaved(self):
        """Unsaved View
        
        Check if the view has unsaved changes
        
        Returns:
            bool -- True if it's unsaved
        """
        return self.view.is_dirty()

    def check_main_requirements(self):
        """Main Requirements
        
        If a sketch has been never unsaved and it's not empty,
        this method will save it with a randon name based in 
        the time in the temp path. If the sketch is empty it
        will not allow the command (compile/uplaod/clean) to
        continue.

        It the sketch hasn't the an IOT extension, it will be
        considerated not IOT so, you can process the file.

        If the file has unsaved changes, it will save it before
        to process the file
        
        Returns:
            bool -- False if any of the requirements fails.
        """
        if(self.is_empty()):
            self.dprint("not_empty_sketch")
            return False

        if(not self.get_file_name()):
            self.save_code_infile()

        if(not self.is_iot()):
            self.derror("not_iot_{0}", self.get_file_name())
            return False

        self.check_unsaved_changes()

        return True

    def check_unsaved_changes(self):
        """Check unsaved changes
        
        Saves the changes if the view is dirty (with chages)
        """

        if(self.is_unsaved()):
            self.view.run_command('save')

    def structurize_project(self):
        """Structure Files
        
        If a project isn't initialized, it need to be checked
        if the open file is inside of the src folder, if it isn't
        the file need to be moved to the src folder
        """
        pio_structure = self.get_structure_option()

        if(pio_structure):
            file_path = self.get_file_path()
            if('src' not in file_path):
                from shutil import move
                
                self.close_file()

                dst = add_folder_to_filepath(file_path, 'src')
                move(file_path, dst)

                self.window.open_file(dst)
                return

        self.override_src()

    def override_src(self):
        """Adds src_dir
        
        When you don't want to keep the platformio file structure, you need to add
        the 'src_dir' flag in the platformio.ini with the path of your sketch/project.
        Here we add that option when platformio structure is not enabled
        """
        from ..libraries.configobj.configobj import ConfigObj
        
        source = {'src_dir': self.get_project_path()}
        ini_path = self.get_ini_path()
        config = ConfigObj(ini_path)

        config['platformio'] = source
        
        config.write()

    def close_file(self):
        """Close File Window
        
        Close the current focused windows in sublime text
        """
        self.window.run_command('close_file')

    def check_board_selected(self):
        """Checks Board Selection
        
        If an environment is stored in the preferences file, it will
        be loaded in the board_id object, if not, it will show the
        quick panel to select the board
        """
        self.board_id = self.get_environment()

        if(not self.board_id):
            selected_boards = self.get_selected_boards()

            if(not selected_boards):
                QuickMenu().quick_boards()
                return

            QuickMenu().quick_environments()
            return

    def check_port_selected(self):
        """Checks Serial Port Selection
        
        If the serial port is stored in the preferences file, it will
        be loaded in the port_id object, if not, it will show the 
        quick panel to select the port
        """
        self.port_id = self.get_serial_port()
        ports_list = serial_port_list()

        port_ready = [port[1] for port in ports_list if self.port_id == port[1]]

        if(not port_ready):
            QuickMenu().quick_serial_ports()
            self.port_id = None

    def check_serial_monitor(self):
        """Check monitor serial
        
        Checks if the monitor serial is currently running
        and close it.

        It will also stores a reference in the preferences (last_action)
        to run the serial monitor next time
        """
        from . import serial
        from .tools import save_setting

        port_id = self.port_id

        if(port_id in serial.serials_in_use):
            serial_monitor = serial.get_serial_monitor(port_id)

            serial_monitor.stop()
            serial.serials_in_use.remove(port_id)
            del serial.serial_monitor_dict[port_id]

            save_setting('run_monitor', True)

    def save_code_infile(self):
        """Save Code

        If the sketch in the current view has been not saved, it generate
        a random name and stores in a temp folder.

        Arguments: view {ST Object} -- Object with multiples options of ST
        """
        from os import path
        from time import time
        from sublime import Region
        from ..libraries.file import File
        from ..libraries.tools import make_folder

        ext = '.ino'

        tmppath = self.get_temp_path()
        filename = str(time()).split('.')[0]
        filepath = path.join(tmppath, filename, 'src')

        make_folder(filepath)

        fullpath = filename + ext
        fullpath = path.join(filepath, fullpath)

        region = Region(0, self.view.size())
        text = self.view.substr(region)
        file = File(fullpath)
        file.write(text)

        self.view.set_scratch(True)
        self.window.run_command('close')
        self.view = self.window.open_file(fullpath)

def add_folder_to_filepath(src_path, new_folder):
    """Add folder
    
    Add a new folder at the end of the given specific path
    
    Arguments:
        src_path {str} -- initial path including the filename
        new_folder {str} -- string to add after the last folder in the path
    
    Returns:
        str -- file path with the new folder added
    """

    folder = path.dirname(src_path)
    file_name = path.basename(src_path)
    new_path = path.join(folder, new_folder, file_name)
    
    return new_path
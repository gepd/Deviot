#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ProjectCheck handles the actions between sublime text and platformio.
Before run a platformio command like initilize, compile or upload, this
class check if the project meets the requirements to proceed with the
command, for example if the current file has been saved, or if it's saved
is in the src folder when the platformio sutrcture options is marked
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

from os import path

from ..platformio.project_recognition import ProjectRecognition

class ProjectCheck(ProjectRecognition):
    def __init__(self):
        super(ProjectCheck, self).__init__()

        self.cwd = self.get_working_project_path()

    def is_iot(self):
        """IOT
        
        Checks if the file in the current view is in the list
        of the IOT types (accepteds) or not
        
        Returns:
            bool -- true if is in the list false if not
        """
        ext = self.get_file_extension()
        accepteds = ['ino', 'pde', 'cpp', 'c', '.S']

        if(ext not in accepteds):
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

    def get_working_project_path(self):
        """Working Path
        
        The working path is where platformio.ini is located
        it's used each time when deviot is compiling the code

        Returns:
            str -- path/working_path
        """
        if(self.is_initialized()):
            ini_path = self.get_ini_path()
            working_path = os.path.dirname(ini_path)
            return working_path

        pio_structure = self.get_structure_option()

        if(pio_structure):
            return self.get_project_path()
        
        return self.get_temp_project_path()

    def structurize_project(self):
        """Structure Files
        
        If a project isn't initialized, it need to be checked
        if the open file is inside of the src folder, if it isn't
        the file need to be moved to the src folder
        """
        if(self.is_initialized()):
            return True

        pio_structure = self.get_structure_option()

        if(pio_structure):
            file_path = self.get_file_path()
            if('src' not in file_path):
                from shutil import move
                
                self.close_file()

                dst = add_folder_to_filepath(file_path, 'src')
                move(file_path, dst)

                self.window.open_file(dst)


    def get_structure_option(self):
        """Pio Structure Option
        
        Check if the platformio structure option is mark as
        true or not
        
        Returns:
            bool -- true to keep working with platformio structure
        """
        return True

    def close_file(self):
        """Close File Window
        
        Close the current focused windows in sublime text
        """
        self.window.run_command('close_file')


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
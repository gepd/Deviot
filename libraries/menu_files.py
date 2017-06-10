#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import os

from . import paths
from .file import File
from ..platformio.pio_bridge import PioBridge

class MenuFiles(PioBridge):
    def __init__(self):
        super(MenuFiles, self).__init__()
        self.create_main_menu()

    def get_template_menu(self, file_name):
        """Template Menu
        
        Get a JSON template file and return it.
        To this option works, the file must be located
        in the Deviot/presets folder
        
        Arguments:
            file_name {str} -- name of the file
        
        Returns:
            json -- data of the file
        """
        file_path = paths.getPresetFile(file_name)
        preset_file = File(file_path)
        preset_data = preset_file.read_json()
        
        return preset_data

    def create_sublime_menu(self, data, menu_name, path):
        """Sublime Menu
        
        Generate a .sublime-menu file who is used by sublime text
        to generate the menu in the menu bar.
        
        Arguments:
            data {json} -- data with the structure of the menu
            menu_name {str} -- the file will be called menu_name.sublime-menu
            path {str} -- where the menu will be located
        """
        from json import dumps
        
        menu_name = menu_name + '.sublime-menu'
        menu_path = os.path.join(path, menu_name)
        
        file = File(menu_path)
        data = dumps(data, sort_keys=True, indent=4)
        file.write(data)

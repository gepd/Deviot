#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import os

from . import paths
from .file import File
from .menu_files import MenuFiles

class TopMenu(MenuFiles):
    def __init__(self):
        super(TopMenu, self).__init__()
        self.create_main_menu()

    def create_main_menu(self):
        """Main Menu
        
        Generates the main menu of the plugin.
        The main menu is built from diferents sources, here
        the diferents sources are called to get the data, the
        data is manipulated (ex. translated) and stored as a
        menu file (menu_name.sublime-menu)
        """
        menu_preset = self.get_template_menu('main_menu.json')
        path = paths.getPluginPath()

        self.create_sublime_menu(menu_preset, 'Main', path)

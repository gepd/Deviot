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
from .I18n import I18n

_ = I18n().translate

class TopMenu(MenuFiles):
    def __init__(self):
        super(TopMenu, self).__init__()

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

        for option in menu_preset:
            option = self.translate_childrens(option)
            for sub in option['children']:
                try:
                    sub = self.translate_childrens(sub)
                except KeyError:
                    pass

        self.create_sublime_menu(menu_preset, 'Main', path)

    def translate_childrens(self, option_dict):
        """Translate Children Menu
        
        Translate a children sublime text menu
        
        Arguments:
            option_dict {dict} -- children to be traslated
        
        Returns:
            dict -- children translated
        """
        for children in option_dict['children']:
            children['caption'] = _(children['caption'])
            try:
                for children_chil in children['children']:
                   children_chil['caption'] = _(children_chil['caption'])
            except:
                pass

        return option_dict

    def make_menu_files(self):
        """Menu Files
        
        Makes each file who needs to be translated like
        the main menu, quick panel, contextual menu
        """
        self.create_main_menu()
        self.create_quick_commands()
        self.create_context_menu()
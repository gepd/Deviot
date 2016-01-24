#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import os
import json

try:
    from . import Serial, Paths
    from .Preferences import Preferences
    from .JSONFile import JSONFile
    from .I18n import I18n
except:
    from libs.Preferences import Preferences
    from libs.JSONFile import JSONFile
    from libs import Serial, Paths
    from libs.I18n import I18n

_ = I18n().translate


class Menu(object):
    '''
    Class to handle the differents option in the plugin menu.
    '''

    def __init__(self):
        '''
        Call the construct of the command library to make the
        differents call by CLI
        '''
        super(Menu, self).__init__()

    def createBoardsMenu(self):
        '''
        Load the JSON file with the list of all boards and re order it
        based on the vendor. after that format the data to operate with
        the standards required for the ST

        Returns: {json array} -- list of all boards to show in the menu
        '''
        vendors = {}
        boards = []

        platformio_data = self.getTemplateMenu(
            file_name='platformio_boards.json', user_path=True)

        if(not platformio_data):
            return

        platformio_data = json.loads(platformio_data)

        # searching data
        for datakey, datavalue in platformio_data.items():
            for infokey, infovalue in datavalue.items():
                vendor = datavalue['vendor']
                if('name' in infokey):
                    temp_info = {}
                    temp_info['caption'] = infovalue
                    temp_info['command'] = 'select_board'
                    temp_info['checkbox'] = True
                    temp_info['args'] = {'board_id': datakey}
                    children = vendors.setdefault(vendor, [])
                    children.append(temp_info)

        # reorganizing data
        for vendor, children in vendors.items():
            children = sorted(children, key=lambda x: x['caption'])
            boards.append({'caption': vendor,
                           'children': children})

        boards = sorted(boards, key=lambda x: x['caption'])

        return boards

    def createEnvironmentMenu(self, empty=False):
        '''
        Get all the boards selected by the user and creates a JSON
        file with the list of all environment selected by the user.
        The file is stored in:
        Packages/User/Deviot/environment/environment.json
        '''
        environments = []
        if(not empty):
            is_native = Preferences().get('native', False)
            type = 'board_id' if not is_native else 'found_ini'
            env_selecs = Preferences().get(type, '')
            env_boards = self.getTemplateMenu(
                'env_boards.json', user_path=True)

            if(not env_boards):
                return

            # search
            for board in env_boards:
                for selected in env_selecs:
                    try:
                        environments.append(board[selected]['children'][0])
                    except:
                        pass

        # save
        env_menu = self.getTemplateMenu(file_name='environment.json')
        env_menu[0]['children'][0]['children'] = environments
        self.saveSublimeMenu(data=env_menu,
                             sub_folder='environment',
                             user_path=True)

    def createSerialPortsMenu(self):
        '''
        Creates a menu list with all serial ports available
        '''
        port_list = Serial.listSerialPorts()

        if not port_list:
            return False

        menu_preset = self.getTemplateMenu(file_name='serial.json')
        menu_ports = []

        for port in port_list:
            menu_ports.append({'caption': port,
                               'command': 'select_port',
                               'checkbox': True,
                               'args': {'id_port': port}})

        menu_preset[0]['children'][0]['children'] = menu_ports

        self.saveSublimeMenu(data=menu_preset,
                             sub_folder='serial',
                             user_path=True)

    def createMainMenu(self):
        '''
        Creates the main menu with the differents options
        including boards, libraries, and user options.
        '''
        boards = self.createBoardsMenu()

        if(not boards):
            return False

        menu_data = self.getTemplateMenu(file_name='menu_main.json')

        # Main Menu
        for first_menu in menu_data[0]:
            for second_menu in menu_data[0][first_menu]:
                if 'caption' in second_menu:
                    second_menu['caption'] = _(second_menu['caption'])
                if 'children' in second_menu:
                    if(second_menu['id'] == 'select_board'):
                        second_menu['children'] = boards

        # sub menu translation (avoiding the boards menu)
        for third_menu in menu_data[0]['children']:
            try:
                for caption in third_menu['children']:
                    caption['caption'] = _(caption['caption'])
                    try:
                        for item in caption['children']:
                            item['caption'] = _(item['caption'])
                    except:
                        pass

            except:
                pass

        self.saveSublimeMenu(data=menu_data)

        env_path = Paths.getSublimeMenuPath(
            'environment', user_path=True)

        if(os.path.isfile(env_path)):
            self.createEnvironmentMenu()

        self.createLanguageMenu()

    def createLanguageMenu(self):
        """
        Creates the language menu options based in the
        translations located in Packages/Deviot/Languages
        """
        menu_language = []
        lang_ids = I18n().getLangIds()
        for id_lang in lang_ids:
            lang_names = I18n().getLangNames(id_lang)
            caption = '%s (%s)' % (lang_names[0], lang_names[1])
            options = {}
            options['caption'] = caption
            options['command'] = 'select_language'
            options['args'] = {'id_lang': id_lang}
            options['checkbox'] = True
            menu_language.append(options)

        # get language menu preset
        menu_preset = self.getTemplateMenu(file_name='language.json')
        # load languages
        menu_preset[0]['children'][0]['children'] = menu_language
        # save data as ST menu
        self.saveSublimeMenu(data=menu_preset,
                             sub_folder='language',
                             user_path=True)

    def getTemplateMenu(self, file_name, user_path=False):
        """
        Get the template menu file to be modified by the different methods

        Arguments
        file_name {string} -name of the file including the extension
        user_path {boolean} -- True: get file from Packages/Deviot/Preset
                            --False: get file from Packages/User/Deviot/Preset
                              (Defaul:False)
        """
        file_path = Paths.getTemplateMenuPath(file_name, user_path)
        preset_file = JSONFile(file_path)
        preset_data = preset_file.getData()
        return preset_data

    def saveTemplateMenu(self, data, file_name, user_path=False):
        """
        Save the menu template in json format

        Arguments:
        data {json} -- st json object with the data of the menu
        file_name {string} -- name of  the file including the extension
        user_path {boolean} -- True: save file in Packages/Deviot/Preset
                            --False: save file in Packages/User/Deviot/Preset
                              (Defaul:False)
        """
        file_path = Paths.getTemplateMenuPath(file_name, user_path)
        preset_file = JSONFile(file_path)
        preset_file.setData(data)
        preset_file.saveData()

    def getSublimeMenu(self, user_path=False):
        """
        Get the data of the different files that make up the main menu

        Keyword Arguments:
        user_path {boolean} -- True: get file from Packages/Deviot/Preset
                            --False: get file from Packages/User/Deviot/Preset
                              (Defaul:False)
        """
        menu_path = Paths.getSublimeMenuPath(user_path)
        menu_file = JSONFile(menu_path)
        menu_data = menu_file.getData()
        return menu_data

    def saveSublimeMenu(self, data, sub_folder=False, user_path=False):
        """
        Save the data in different files to make up the main menu

        Arguments:
        data {json} -- json st data to create the menu

        Keyword Arguments:
        sub_folder {string/bool} -- name of the sub folder to save the file
                                 -- (default: False)
        user_path {boolean} -- True: Save file in Packages/Deviot/Preset
                            -- False: Save file in Packages/User/Deviot/Preset
                               (Defaul:False)
        """
        menu_file_path = Paths.getSublimeMenuPath(sub_folder, user_path)
        file_menu = JSONFile(menu_file_path)
        file_menu.setData(data)
        file_menu.saveData()

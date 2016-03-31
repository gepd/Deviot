#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import os
import json
import glob
from re import search

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
                    temp_info['command'] = 'deviot_select_board'
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

    def createLibraryImportMenu(self):
        """
        Creates the import library menu
        this method search in the user and core libraries
        """
        library_paths = Paths.getLibraryFolders()
        added_lib = []
        children = []

        # get preset
        menu_import_lib = self.getTemplateMenu(file_name='import_library.json')

        for library_dir in library_paths:
            # add separator
            if 'arduinoteensy' not in library_dir:
                temp_info = {}
                temp_info['caption'] = '-'
                children.append(temp_info)
            sub_path = glob.glob(library_dir)

            # search in sub path
            for library in sub_path:

                # Add core libraries
                if '__cores__' in library:
                    core_subs = os.path.join(library, '*')
                    core_subs = glob.glob(core_subs)
                    for core_sub in core_subs:
                        core_sub_subs = os.path.join(core_sub, '*')
                        core_sub_subs = glob.glob(core_sub_subs)
                        for core_lib in core_sub_subs:
                            caption = os.path.basename(core_lib)
                            if caption not in added_lib:
                                temp_info = {}
                                temp_info['caption'] = caption
                                temp_info['command'] = 'add_library'
                                temp_info['args'] = {'library_path': library}
                                children.append(temp_info)
                                added_lib.append(caption)

                # the rest of the libraries
                caption = os.path.basename(library)

                # get library name from json file
                pio_libs = os.path.join('platformio', 'lib')
                if pio_libs in library:

                    # get library json details
                    library_json = os.path.join(library, 'library.json')
                    if (not os.path.exists(library_json)):
                        library_json = os.path.join(
                            library, 'library.properties')

                    # when there´s json content, read it
                    json = JSONFile(library_json)
                    json = json.getData()
                    if (json != {}):
                        caption = json['name']

                if caption not in added_lib and '__cores__' not in caption:
                    temp_info = {}
                    temp_info['caption'] = caption
                    temp_info['command'] = 'add_library'
                    temp_info['args'] = {'library_path': library}
                    children.append(temp_info)
                    added_lib.append(caption)

        # save file
        menu_import_lib[0]['children'][0]['children'] = children
        self.saveSublimeMenu(data=menu_import_lib,
                             sub_folder='import_library',
                             user_path=True)

    def createLibraryExamplesMenu(self):
        """
        Shows the examples of the library in a menu
        """
        examples = []
        children = []

        library_paths = Paths.getLibraryFolders()
        for path in library_paths:
            sub_paths = glob.glob(path)
            for sub in sub_paths:
                sub = os.path.join(sub, '*')
                libs = glob.glob(sub)
                for lib in libs:
                    caption = os.path.basename(os.path.dirname(lib))
                    new_caption = search(r"^(\w+)_ID?", caption)
                    if(new_caption is not None):
                        caption = new_caption.group(1)
                    if os.path.isdir(lib) and os.listdir(lib) and 'examples' in lib:
                        file_examples = os.path.join(lib, '*')
                        file_examples = glob.glob(file_examples)
                        for file in file_examples:
                            caption_example = os.path.basename(file)
                            temp_info = {}
                            temp_info['caption'] = caption_example
                            temp_info['command'] = 'open_example'
                            temp_info['args'] = {'example_path': file}
                            children.append(temp_info)
                        temp_info = {}
                        temp_info['caption'] = caption
                        temp_info['children'] = children
                        examples.append(temp_info)
                        children = []
            examples.append({'caption': '-'})

        # get preset
        menu_lib_example = self.getTemplateMenu(file_name='examples.json')

        # save file
        menu_lib_example[0]['children'][0]['children'] = examples
        self.saveSublimeMenu(data=menu_lib_example,
                             sub_folder='library_example',
                             user_path=True)

    def createSerialPortsMenu(self):
        '''
        Creates a menu list with all serial ports available
        '''
        port_list = Serial.listSerialPorts()
        ip_port = Preferences().get('ip_port', '')

        if(ip_port):
            port_list.insert(0, ip_port)

        menu_preset = self.getTemplateMenu(file_name='serial.json')
        menu_ports = [
            {"caption": _("menu_add_ip"), "command": "add_serial_ip"}]

        for port in port_list:
            temp_info = {}
            temp_info['caption'] = port
            temp_info['command'] = 'select_port'
            temp_info['checkbox'] = True
            temp_info['args'] = {'id_port': port}
            menu_ports.append(temp_info)

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

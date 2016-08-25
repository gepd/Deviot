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

from . import Paths
from .Preferences import Preferences
from .JSONFile import JSONFile
from .I18n import I18n


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
        from . import Tools

        file = "platformio_boards.json"
        boards = [[_("select_board_list").upper()]]
        data = self.getTemplateMenu(file_name=file, user_path=True)

        list_env = Preferences().get('board_id', [])
        list_env.extend(Tools.getEnvFromFile())
        list_env = sorted(list(set(list_env)))

        if(not data):
            return

        platformio_data = json.loads(data)

        # searching data
        try:
            for datakey, datavalue in platformio_data.items():
                try:
                    caption = "+ " + datavalue['name']
                    for env in list_env:
                        if(datakey == env):
                            caption = "- " + datavalue['name']
                    vendor = "%s | %s" % (datavalue['vendor'], datakey)
                    boards.append([caption, vendor])
                except:
                    pass
        except:  # PlatformIO 3
            for data in platformio_data:
                caption = "+ " + data['name']
                for env in list_env:
                    if(data['id'] == env):
                        caption = "- " + data['name']
                vendor = "%s | %s" % (data['vendor'], data['id'])
                boards.append([caption, vendor])

        return boards

    def getEnvironments(self):
        '''
        Get all the boards selected by the user and creates a JSON
        file with the list of all environment selected by the user.
        The file is stored in:
        Packages/User/Deviot/environment/environment.json
        '''

        from . import Tools

        selected_index = 0
        environments = [[_("select_env_list").upper()]]
        index = 0

        list_env = Preferences().get('board_id', [])
        list_env.extend(Tools.getEnvFromFile())
        list_env = sorted(list(set(list_env)))

        env_selected = Tools.getEnvironment()
        env_data = self.getTemplateMenu(
            file_name='platformio_boards.json', user_path=True)
        env_data = json.loads(env_data)

        try:
            for key, value in env_data.items():
                try:
                    id = key
                    caption = value['name']
                    vendor = value['vendor']

                    for selected in list_env:
                        if(selected == id):
                            vendor = "%s | %s" % (vendor, id)
                            environments.append([caption, vendor])

                            if(selected == env_selected):
                                selected_index = index + 1
                            index += 1
                except:
                    pass
        except:  # PlatformIO 3
            for value in env_data:
                id = value['id']
                caption = value['name']
                vendor = value['vendor']

                for selected in list_env:
                    if(selected == id):
                        vendor = "%s | %s" % (vendor, id)
                        environments.append([caption, vendor])

                        if(selected == env_selected):
                            selected_index = index + 1
                        index += 1

        return [environments, selected_index]

    def createLibraryImportMenu(self):
        """
        Creates the import library menu
        this method search in the user and core libraries
        """
        from . import Tools

        sel_env = Tools.getEnvironment()

        file = "platformio_boards.json"
        data = self.getTemplateMenu(file_name=file, user_path=True)
        data = json.loads(data)

        # check current platform
        try:
            platform = data[sel_env]['platform'].lower()
        except:
            platform = 'all'

        library_paths = Paths.getLibraryFolders(platform)
        added_lib = [[_("select_library").upper()]]
        check_list = []

        # get preset
        for library_dir in library_paths:
            # add separator
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
                            if caption not in check_list:
                                caption = os.path.basename(core_lib)
                                added_lib.append([caption, library])
                                check_list.append(caption)

                # the rest of the libraries
                caption = os.path.basename(library)

                # get library name from json file
                pio_libs = os.path.join('platformio', 'lib')
                if pio_libs in library:
                    # get library json details
                    json_file = os.path.join(library, 'library.json')
                    if not os.path.exists(json_file):
                        json_file = os.path.join(library, 'library.properties')

                    # when there´s json content, read it
                    data = JSONFile(json_file)
                    data = data.getData()
                    if (data != {}):
                        caption = data['name']

                if caption not in added_lib and '__cores__' not in caption and
                caption not in check_list:
                    added_lib.append([caption, library])
                    check_list.append(caption)

        if(len(added_lib) <= 1):
            added_lib = [[_("menu_not_libraries")]]

        return added_lib

    def createLibraryExamplesMenu(self):
        """
        Shows the examples of the library in a menu
        """
        from . import Tools

        sel_env = Tools.getEnvironment()

        data = self.getTemplateMenu(
            file_name='platformio_boards.json', user_path=True)
        data = json.loads(data)

        # check current platform
        try:
            platform = data[sel_env]['platform'].lower()
        except:
            platform = 'all'

        examples = [[_("select_library").upper()]]
        check_list = []

        library_paths = Paths.getLibraryFolders(platform)

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
                    if 'examples' in lib and os.path.isdir(lib) and
                    os.listdir(lib) and caption not in check_list:
                        examples.append([caption, lib])
                        check_list.append(caption)

        if(len(examples) <= 1):
            added_lib = [[_("menu_not_libraries")]]

        return examples

    def createMainMenu(self):
        '''
        Creates the main menu with the differents options
        including boards, libraries, and user options.
        '''
        from .Tools import getJSONBoards

        getJSONBoards()
        menu_data = self.getTemplateMenu(file_name='menu_main.json')

        # Main Menu
        for first_menu in menu_data[0]:
            for second_menu in menu_data[0][first_menu]:
                if 'caption' in second_menu:
                    second_menu['caption'] = _(second_menu['caption'])

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
        self.createLanguageMenu()
        self.translateContextMenu()

    def translateContextMenu(self):
        """
        Translate the context menu getting the preset file from context.json
        """
        contex_file = self.getTemplateMenu(file_name='context.json')

        for contex in contex_file:
            try:
                contex['caption'] = _(contex['caption'])
            except:
                pass

        plugin = Paths.getPluginPath()
        context_path = os.path.join(plugin, 'Context.sublime-menu')
        preset_file = JSONFile(context_path)
        preset_file.setData(contex_file)
        preset_file.saveData()

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

#!/usr/bin/env python
#-*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import os
import inspect

current_file = os.path.abspath(inspect.getfile(inspect.currentframe()))

# Get the path of deviot plugin
def getPluginPath():
	plugin_path = os.path.dirname(current_file)
	return plugin_path

# Get Sublime Text package folder
def getPackagesPath():
    plugin_path = getPluginPath()
    packages_path = os.path.dirname(plugin_path)
    return packages_path

# Get the path of the Preset folder
def getPresetPath():
	plugin_path = getPluginPath()
	preset_path = os.path.join(plugin_path, 'Preset')
	return preset_path

# Get deviot path from user folder
def getDeviotUserPath():
    packages_path = getPackagesPath()
    user_path = os.path.join(packages_path, 'User')
    deviot_user_path = os.path.join(user_path, 'Deviot')
    
    if(not os.path.isdir(deviot_user_path)):
            os.makedirs(deviot_user_path)

    return deviot_user_path

def getDeviotBoardsPath():
    deviot_user_path = getDeviotUserPath()
    boards_path = os.path.join(deviot_user_path,'Boards.json')
    return boards_path

def getDeviotMenuPath(sub_folder=False):
    deviot_user_path = getDeviotUserPath()

    if(sub_folder):
        deviot_user_path = os.path.join(deviot_user_path,sub_folder)

        if(not os.path.isdir(deviot_user_path)):
            os.makedirs(deviot_user_path)

    menu_path = os.path.join(deviot_user_path, 'Main.sublime-menu')

    return menu_path


def getPreferencesFile():
    deviot_user_path = getDeviotUserPath()
    preferences_path = os.path.join(deviot_user_path,'Preferences.Deviot-settings')
    return preferences_path

def getMainJSONFile():
    preset_path = getPresetPath()
    main_file_path = os.path.join(preset_path,'menu_main.json')
    return main_file_path

def getCurrentFilePath(view):
    window = view.window()
    views = window.views()

    if view not in views:
        view = window.active_view()

    return view.file_name()

def getCWD(file_path):
    folder_path = os.path.dirname(file_path)
    return folder_path
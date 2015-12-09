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
    return deviot_user_path

def getDeviotBoardsPath():
    deviot_user_path = getDeviotUserPath()
    boards_path = os.path.join(deviot_user_path,'Boards.json')
    return boards_path

def getPreferencesFile():
    deviot_user_path = getDeviotUserPath()
    preferences_path = os.path.join(deviot_user_path,'Preferences.Deviot-settings')
    return preferences_path
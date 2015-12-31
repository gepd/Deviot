#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import os
import inspect
import sublime

if(int(sublime.version()) < 3000):
    import DeviotTools
else:
    from . import DeviotTools

current_file = os.path.abspath(inspect.getfile(inspect.currentframe()))

# Get the path of deviot plugin


def getPluginPath():
    plugin_path = os.path.dirname(current_file)
    return plugin_path

# Get the package sublime text path


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

# get the library user folder


def getLibraryPath():
    user_path = getDeviotUserPath()
    library_path = os.path.join(user_path, 'libraries')

    if(not os.path.isdir(library_path)):
        os.makedirs(library_path)

    return library_path


def getTemplateMenuPath(file_name, user_path=False):
    if(not user_path):
        preset_path = getPresetPath()
    else:
        preset_path = getDeviotUserPath()
        preset_path = os.path.join(preset_path, 'Preset')

        if(not os.path.isdir(preset_path)):
            os.makedirs(preset_path)
    menu_path = os.path.join(preset_path, file_name)

    return menu_path


def getSublimeMenuPath(sub_folder=False, user_path=False):
    menu_path = getPluginPath()
    if(user_path):
        menu_path = getDeviotUserPath()

    if(sub_folder):
        menu_path = os.path.join(menu_path, sub_folder)

        if(not os.path.isdir(menu_path)):
            os.makedirs(menu_path)

    menu_path = os.path.join(menu_path, 'Main.sublime-menu')

    return menu_path


def getPreferencesFile():
    deviot_user_path = getDeviotUserPath()
    preferences_path = os.path.join(
        deviot_user_path, 'Preferences.Deviot-settings')
    return preferences_path


def getJSONFile(file_name):
    preset_path = getPresetPath()
    main_file_path = os.path.join(preset_path, file_name)  # 'menu_main.json'
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


def getParentCWD(file_path):
    folder_path = os.path.dirname(file_path)
    parent = os.path.dirname(folder_path)
    return parent


def getDeviotTmpPath(file_name=False):
    tmp_path = '/tmp'
    os_name = DeviotTools.getOsName()
    if os_name == 'windows':
        tmp_path = os.environ['tmp']

    tmp_path = os.path.join(tmp_path, 'Deviot')

    if(file_name):
        tmp_path = os.path.join(tmp_path, file_name)

    if(not os.path.isdir(tmp_path)):
        os.makedirs(tmp_path)
    return tmp_path

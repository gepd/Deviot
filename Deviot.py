# !/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

from os import path
from sublime_plugin import EventListener

from .commands import *
from .platformio.update import Update
from .beginning.pio_install import PioInstall
from .libraries.tools import get_setting, save_setting, get_phantoms, del_phantom
from .libraries.paths import getBoardsFileDataPath, getMainMenuPath
from .libraries.preferences_bridge import PreferencesBridge
from .libraries.project_check import ProjectCheck

def plugin_loaded():
    PioInstall()
    Update().check_update_async()

    menu_path = getMainMenuPath()
    compile_lang = get_setting('compile_lang', True)
    
    if(compile_lang or not path.exists(menu_path)):
        from .libraries.top_menu import TopMenu
        TopMenu().make_menu_files()
        save_setting('compile_lang', False)

class DeviotListener(EventListener):
    def on_activated(self, view):
        PreferencesBridge().set_status_information()
    
    def on_close(self, view):
        from .libraries import serial
        
        window_name = view.name()
        search_id = window_name.split(" | ")

        if(len(search_id) > 1 and search_id[1] in serial.serials_in_use):
            port_id = search_id[1]
            serial_monitor = serial.serial_monitor_dict.get(port_id, None)
            serial_monitor.stop()
            del serial.serial_monitor_dict[port_id]

    def on_modified(self, view):
        """On modify file
        
        checks the phantoms in the current view and remove it
        when it's neccesary
        
        Arguments:
            view {obj} -- sublime text object
        """
        phantoms = get_phantoms()
        is_iot = ProjectCheck().is_iot()

        if(not len(phantoms) and not is_iot):
            return

        line, column = view.rowcol(view.sel()[0].begin())
        pname = 'error' + str(line + 1)

        if(pname in phantoms):
            del_phantom(pname)
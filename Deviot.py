# !/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

from os import path
from sublime_plugin import EventListener

from .commands import *
from .beginning.pio_install import PioInstall
from .libraries.tools import get_setting, save_setting
from .libraries.paths import getBoardsFileDataPath, getMainMenuPath
from .platformio.pio_bridge import PioBridge

def plugin_loaded():
    PioInstall()

    boards_file = getBoardsFileDataPath()

    if(not path.exists(boards_file)):
        PioBridge().save_boards_list()

    menu_path = getMainMenuPath()
    compile_lang = get_setting('compile_lang', True)
    
    if(compile_lang or not path.exists(menu_path)):
        from .libraries.top_menu import TopMenu
        TopMenu().create_main_menu()
        save_setting('compile_lang', False)

class DeviotListener(EventListener):
    def on_activated(self, view):
        #
        pass
    
    def on_close(self, view):
        from .libraries import serial
        
        window_name = view.name()
        search_id = window_name.split(" | ")

        if(len(search_id) > 1 and search_id[1] in serial.serials_in_use):
            port_id = search_id[1]
            serial_monitor = serial.serial_monitor_dict.get(port_id, None)
            serial_monitor.stop()
            del serial.serial_monitor_dict[port_id]
                
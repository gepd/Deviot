# !/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

from os import path
from sublime import windows
from sublime_plugin import EventListener

from .commands import *
from .platformio.update import Update
from .beginning.pio_install import PioInstall
from .libraries.tools import get_setting, save_setting, set_deviot_syntax
from .libraries.paths import getBoardsFileDataPath, getMainMenuPath, getPluginPath
from .libraries.preferences_bridge import PreferencesBridge
from .libraries.project_check import ProjectCheck

def plugin_loaded():
    # Load or fix the right deviot syntax file 
    for window in windows():
        for view in window.views():
            set_deviot_syntax(view)

    # Install PlatformIO
    PioInstall()

    # Search updates
    Update().check_update_async()

    menu_path = getMainMenuPath()
    compile_lang = get_setting('compile_lang', True)
    
    if(compile_lang or not path.exists(menu_path)):
        from .libraries.top_menu import TopMenu
        TopMenu().make_menu_files()
        save_setting('compile_lang', False)

    # check if the syntax file exist
    deviot_syntax = getPluginPath()
    syntax_path = path.join(deviot_syntax, 'deviot.sublime-syntax')

    if(not path.exists(syntax_path)):
        active_window().run_command('deviot_rebuild_syntax')


class DeviotListener(EventListener):
    def on_load(self, view):
        set_deviot_syntax(view)

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
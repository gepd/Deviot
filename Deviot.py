# !/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

from os import path, remove
from shutil import rmtree
from sublime import message_dialog
from sublime_plugin import EventListener

from .commands import *
from .platformio.update import Update
from .beginning.pio_install import PioInstall
from .libraries.tools import get_setting, save_setting
from .libraries.syntax import Syntax
from .libraries.paths import getMainMenuPath, getPackagesPath
from .libraries.paths import getDeviotUserPath, getPluginName
from .libraries.preferences_bridge import PreferencesBridge
from .libraries.project_check import ProjectCheck

package_name = getPluginName()

def plugin_loaded():
    # Install PlatformIO
    PioInstall()

    # Search updates
    Update().check_update_async()

    # check syntax files
    Syntax().check_syntax_file()

    # Load or fix the right deviot syntax file 
    Syntax().paint_iot_views()

    menu_path = getMainMenuPath()
    compile_lang = get_setting('compile_lang', True)
    
    if(compile_lang or not path.exists(menu_path)):
        from .libraries.top_menu import TopMenu
        TopMenu().make_menu_files()
        save_setting('compile_lang', False)

    from package_control import events
    
    # alert when deviot was updated
    if(events.post_upgrade(package_name)):
        from .libraries.I18n import I18n
        save_setting('compile_lang', True)
        message = I18n().translate("reset_after_upgrade")
        message_dialog(message)

def plugin_unloaded():
    from package_control import events

    if events.remove(package_name):
        # remove settings
        packages = getPackagesPath()
        st_settings = path.join(packages, 'User', 'deviot.sublime-settings')
        if(path.exists(st_settings)):
            remove(st_settings)

        # remove deviot user folder
        user = getDeviotUserPath()
        if(path.isdir(user)):
            rmtree(user)

class DeviotListener(EventListener):
    def on_activated(self, view):
        PreferencesBridge().set_status_information()
    
    def on_close(self, view):
        # remove open used serials ports
        from .libraries import serial
        
        window_name = view.name()
        search_id = window_name.split(" | ")

        if(len(search_id) > 1 and search_id[1] in serial.serials_in_use):
            port_id = search_id[1]
            serial_monitor = serial.serial_monitor_dict.get(port_id, None)
            serial_monitor.stop()
            del serial.serial_monitor_dict[port_id]
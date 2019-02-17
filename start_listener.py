# !/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import sys
import sublime
from os import path, remove
from shutil import rmtree
from sublime_plugin import EventListener

from .commands import *

try:
    from .api import deviot
    from .libraries.tools import save_setting
    from .libraries.preferences_bridge import PreferencesBridge
    from .libraries import messages
except ImportError:
    pass

package_name = deviot.plugin_name()

def plugin_loaded():
    window = sublime.active_window()

    # Checks if deviot is installed
    window.run_command("deviot_check_requirements")

    # Searchs updates
    window.run_command("deviot_check_pio_updates")

    # Checks syntax files
    window.run_command("check_syntax_file")

    # Load or fix the right deviot syntax file
    window.run_command("paint_iot_views")

    # Checks if menu files exits
    window.run_command("check_menu_files")

    try:
        from package_control import events

        # alert when deviot was updated
        if(events.post_upgrade(package_name)):
            from .libraries.I18n import I18n

            save_setting('compile_lang', True)

            message = I18n().translate("reset_after_upgrade")
            sublime.message_dialog(message)
    except ImportError:
        pass

def plugin_unloaded():
    from package_control import events

    if events.remove(package_name):
        # remove settings
        packages = deviot.packages_path()
        st_settings = path.join(packages, 'User', 'deviot.sublime-settings')
        if(path.exists(st_settings)):
            remove(st_settings)

        # remove deviot user folder
        user = deviot.user_plugin_path()
        if(path.isdir(user)):
            rmtree(user)


# plugin_unload is not working so if the status bar color
#  folder is present when ST starts, it will remove it.
try:
    plugin = deviot.packages_path()
    status_color_folder = path.join(plugin, 'User', 'Status Color')
    rmtree(status_color_folder)
except OSError:
    pass


class DeviotListener(EventListener):
    def on_activated(self, view):
        PreferencesBridge().set_status_information()

    def on_pre_close(self, view):
        # run on_pre_close to get the window instance
        try:
            name = view.name()
            messages.session[name].on_pre_close(view)
        except:
            pass

    def on_close(self, view):
        # close empty panel
        try:
            name = view.name()
            messages.session[name].on_close(view)
        except:
            pass

        # remove open used serials ports
        from .libraries import serial

        window_name = view.name()
        search_id = window_name.split(" | ")

        if(len(search_id) > 1 and search_id[1] in serial.serials_in_use):
            from .libraries import status_color

            status_color.set('error', 3000)
            port_id = search_id[1]
            serial_monitor = serial.serial_monitor_dict.get(port_id, None)
            serial_monitor.stop()
            del serial.serial_monitor_dict[port_id]

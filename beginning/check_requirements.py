#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import sublime_plugin

from re import sub
from threading import Thread

from .. import deviot
from ..libraries.I18n import I18n
from ..libraries.syntax import Syntax
from ..libraries.thread_progress import ThreadProgress

_version = ''
_symlink = 'python2'


class DeviotCheckRequirementsCommand(sublime_plugin.WindowCommand):
    def run(self):
        thread = Thread(target=self.check)
        thread.start()
        ThreadProgress(thread, 'processing', '')

    def check(self):
        # check if the plugin was installed
        installed = deviot.get_sysetting('installed', False)
        if(bool(installed)):
            return

        Syntax()

        if(not self.check_python()):
            return

        if(not self.check_pio()):
            from .install_pio import InstallPIO

            InstallPIO()

    def get_python_version(self, symlink='python'):
        """
        Gets installed python version
        """
        cmd = [symlink, '--version']
        out = deviot.run_command(cmd)
        return out

    def check_python(self):
        """Python requirement
        Check if python 2 is installed
        """
        global _version

        _version = None

        out = self.get_python_version()
        if(out[0] == 0):
            _version = sub(r'\D', '', out[1])

        if(_version and int(_version[0]) is 3):
            self.check_symlink()

        # show error and link to download
        if(out[0] > 0 or int(_version[0]) is 3):
            translate = I18n().translate
            msg = translate('deviot_need_python')
            btn = translate('button_download_python')
            url = 'https://www.python.org/downloads/'

            open_link = sublime.ok_cancel_dialog(msg, btn)
            if(open_link):
                sublime.run_command('open_url', {'url': url})

            return False
        return True

    def check_symlink(self):
        """Arch Linux

        Check if python 2 is used with a symlink it's
        commonly used in python2. When it's used it's
        stored in a config file to be used by the plugin
        """
        global _symlink

        out = self.get_python_version(_symlink)
        if(out[0] == 1):
            dprint("symlink_detected")
            deviot.save_sysetting('symlink', _symlink)

    def check_pio(self):
        """PlarformIO

        Check if platformIO is already installed in the machine
        """
        global dprint

        # normal check
        cmd = ['--version']
        cmd = deviot.pio_command(cmd)

        out = deviot.run_command(cmd)
        status = out[0]

        if(status > 0):
            # check with edefult environment paths
            env = deviot.environment_paths()
            out = deviot.run_command(cmd[:-1], env_paths=env)
            status = out[0]

        if(status is 0):
            deviot.save_sysetting('installed', True)
            # deviot.save_sysetting('external_bins', True)
            deviot.save_sysetting('env_paths', env)
            return True
        return False

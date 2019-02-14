#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import logging
import sublime
import sublime_plugin

from re import sub
from threading import Thread

from ..api import deviot
from ..libraries.I18n import I18n
from ..libraries.syntax import Syntax
from ..libraries.thread_progress import ThreadProgress

_version = ''
_symlink = 'python2'

logger = logging.getLogger('Deviot')


class DeviotCheckRequirementsCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.installed = deviot.get_sysetting('installed', False)

        # set level depending on the plugin installation status
        if(not self.installed):
            level = logging.DEBUG
        else:
            level = logging.ERROR

        logger.setLevel(level)

        logger.debug("Command executed")

        thread = Thread(target=self.check)
        thread.start()
        ThreadProgress(thread, 'processing', '')

    def check(self):
        logger.debug("New thread started")
        # check if the plugin was installed
        logger.debug("Installed: %s1", self.installed)
        if(bool(self.installed)):
            return

        Syntax()

        if(not self.check_python()):
            return

        from . import install_pio

        if(not self.check_pio()):
            install_pio.InstallPIO()
        else:
            install_pio.already_installed()

    def get_python_version(self, symlink='python'):
        """
        Gets installed python version
        """
        logger.debug("get_python_version")

        version = "0"

        cmd = [symlink, "--version"]

        logger.debug("cmd: %s", cmd)

        out = deviot.run_command(cmd)

        logger.debug("output: %s", out)

        if(out[0] == 0):
            version = sub(r'\D', '', out[1])

        logger.debug("return: %s", version)

        return version

    def check_python(self):
        """Python requirement
        Check if python 2 is installed
        """
        logger.debug("check_python")

        global _version

        _version = self.get_python_version()

        if(_version == "0"):
            self.check_symlink()

        # show error and link to download
        if(_version == "0"):
            logger.debug("no python detected")

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
        logger.debug("check_symlink")

        global _version
        global _symlink

        _version = self.get_python_version(_symlink)

        if(_version[0] == "2"):
            logger.debug("symlink detected")

            deviot.save_sysetting('symlink', _symlink)

            logger.debug("symlink setting stored")

    def check_pio(self):
        """PlarformIO

        Check if platformIO is already installed in the machine
        """
        logger.debug("check_pio")

        global dprint
        save_env = False

        # normal check
        cmd = ['--version']
        cmd = deviot.pio_command(cmd)

        logger.debug("cmd: %s", cmd)

        out = deviot.run_command(cmd)
        status = out[0]

        if(status > 0):
            # check with default environment paths
            env = deviot.environment_paths()

            logger.debug("check pio with extra env PATHs")
            logger.debug("extra paths: %s", env)

            out = deviot.run_command(cmd[:-1], env_paths=env)
            logger.debug("output: %s", out)
            status = out[0]
            save_env = True

        if(status is 0):
            deviot.save_sysetting('installed', True)
            logger.debug("PIO Detected, setup finished")

            if(save_env):
                deviot.save_sysetting('env_paths', env)
                logger.debug("env_paths stored in setting file")
            return True
        return False

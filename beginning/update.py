#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

from re import sub
import sublime_plugin

from .. import deviot
from ..libraries.messages import Messages
from ..libraries.thread_progress import ThreadProgress


class DeviotCheckPioUpdatesCommand(sublime_plugin.WindowCommand):
    def run(self):
        Update().check_update_async()


class DeviotUpdatePioCommand(sublime_plugin.WindowCommand):
    def run(self):
        Update().update_async()


class DeviotDevPioCommand(sublime_plugin.WindowCommand):
    def run(self):
        Update().developer_async()


class Update:
    """Update PlatFormIO

    Class to upgrade platformIO (update_pio) or install the
    developer branch (developer_pio) to avoid block the sublime
    text UI both function are run in a separate thread (async)
    update_asyc, developer_async

    """
    def __init__(self):
        super(Update, self).__init__()

        self.cwd = None
        self.dprint = None
        self.env_paths = deviot.get_sysetting('env_paths', False)

    def show_feedback(self):
        messages = Messages()
        messages.initial_text("_deviot_{0}", deviot.version())
        messages.create_panel()

        self.dprint = messages.print

    def update_pio(self):
        """Update PlatformIO

        Update platformIO to the last version (block thread)
        """
        self.show_feedback()
        self.dprint('searching_pio_updates')

        cmd = deviot.pio_command(['upgrade'])
        out = deviot.run_command(cmd)
        self.dprint(out[1])

    def update_async(self):
        """New Thread Execution

        Starts a new thread to run the update_pio method
        """
        from threading import Thread

        thread = Thread(target=self.update_pio)
        thread.start()
        ThreadProgress(thread, 'processing', '')

    def developer_async(self):
        """New Thread Execution

        Starts a new thread to run the developer_pio method
        """
        from threading import Thread

        thread = Thread(target=self.developer_pio)
        thread.start()
        ThreadProgress(thread, 'processing', '')

    def developer_pio(self):
        """Developer

        Uninstall the current version of platformio and install
        a version based in the preference of the user, it can be
        the stable or developer version
        """
        self.show_feedback()
        self.dprint('uninstall_old_pio')

        cmd = ['pip', 'uninstall', '--yes', 'platformio']
        out = deviot.run_command(cmd)

        developer = deviot.get_sysetting('pio_developer', False)

        if(not developer):
            self.dprint('installing_dev_pio')
            option = 'https://github.com/platformio/' \
                     'platformio/archive/develop.zip'
        else:
            self.dprint('installing_stable_pio')
            option = 'platformio'

        cmd = deviot.prepare_command(['pip', 'install', '-U', option])
        out = deviot.run_command(cmd)

        if(out[0] == 0):
            self.dprint('button_ok')
            deviot.save_sysetting('pio_developer', not developer)
        else:
            self.dprint('setup_error')

    def check_update_async(self):
        """New Thread Execution

        Starts a new thread to run the check_update method
        """
        from threading import Thread

        thread = Thread(target=self.check_update)
        thread.start()
        ThreadProgress(thread, 'processing', '')

    def check_update(self):
        """Check update

        Checks for platformio updates each 5 days.
        To know what is the last version of platformio
        pypi is checked
        """
        installed = deviot.get_sysetting('installed', False)
        if(not installed):
            return

        from datetime import datetime, timedelta

        date_now = datetime.now()
        last_check = deviot.get_sysetting('last_check_update', False)

        try:
            last_check = datetime.strptime(last_check, '%Y-%m-%d %H:%M:%S.%f')

            if(date_now < last_check):
                return
        except TypeError:
            pass

        if(not last_check or date_now > last_check):
            last_check = date_now + timedelta(5, 0)  # 5 days
            deviot.save_sysetting('last_check_update', str(last_check))

        cmd = deviot.pio_command(['--version'])
        out = deviot.run_command(cmd, env_paths=self.env_paths)

        pio_version = int(sub(r'\D', '', out[1]))
        last_pio_version = self.online_pio_version()

        if(pio_version < last_pio_version):
            from sublime import ok_cancel_dialog
            from ..libraries.I18n import I18n

            translate = I18n().translate

            update = ok_cancel_dialog(translate('new_pio_update{0}{1}',
                                                last_pio_version,
                                                pio_version),
                                      translate('update_button'))

            if(update):
                self.show_feedback()
                self.update_pio()

    def online_pio_version(self):
        from urllib.request import Request
        from urllib.request import urlopen
        from urllib.error import HTTPError
        from json import loads

        try:
            url = 'https://pypi.python.org/pypi/platformio/json'
            req = Request(url, headers=deviot.header())
            response = urlopen(req)
            pypi_list = loads(response.read().decode())
            last_pio_version = pypi_list['info']['version']
        except (KeyError, HTTPError) as e:
            return 0

        return int(sub(r'\D', '', last_pio_version))

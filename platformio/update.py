#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

from .command import Command
from ..libraries import __version__ as version
from ..libraries.tools import create_command, get_sysetting, save_sysetting
from ..libraries.messages import Messages
from ..beginning.pio_install import run_command
from ..libraries.thread_progress import ThreadProgress
from ..libraries.I18n import I18n


class Update(Command):
    """Update PlatFormIO
    
    Class to upgrade platformIO (update_pio) or install the
    developer branch (developer_pio) to avoid block the sublime
    text UI both function are run in a separate thread (async)
    update_asyc, developer_async

    
    Extends:
        Command
    """
    def __init__(self):
        super(Update, self).__init__()

        self.cwd = None
        self.dprint = None
        self.translate = I18n().translate

    def show_feedback(self):
        messages = Messages()
        messages.create_panel()

        self.dprint = messages.print

    def update_pio(self):
        """Update PlatformIO
        
        Update platformIO to the last version (block thread)
        """
        self.show_feedback()
        self.dprint('searching_pio_updates')

        cmd = ['upgrade']
        out = run_command(cmd, prepare=True)
        self.dprint(out[1])

    def update_async(self):
        """New Thread Execution
        
        Starts a new thread to run the update_pio method
        """
        from threading import Thread

        thread = Thread(target=self.update_pio)
        thread.start()
        ThreadProgress(thread, self.translate('processing'), '')

    def developer_async(self):
        """New Thread Execution
        
        Starts a new thread to run the developer_pio method
        """
        from threading import Thread

        thread = Thread(target=self.developer_pio)
        thread.start()
        ThreadProgress(thread, self.translate('processing'), '')

    def developer_pio(self):
        """Developer
        
        Uninstall the current version of platformio and install
        a version based in the preference of the user, it can be
        the stable or developer version
        """
        self.show_feedback()
        self.dprint('uninstall_old_pio')

        cmd = ['pip','uninstall', '--yes','platformio']
        out = run_command(cmd)

        if(get_sysetting('pio_developer', False)):
            self.dprint('installing_dev_pio')
            option = 'https://github.com/platformio/' \
            'platformio/archive/develop.zip'
        else:
            self.dprint('installing_stable_pio')
            option = 'platformio'

        cmd = create_command(['pip','install', '-U', option])
        out = run_command(cmd)
        
        if(out[0] == 0):
            self.dprint('button_ok')
            set_sysetting('pio_developer', True)
        else:
            self.dprint('setup_error')

    def check_update_async(self):
        """New Thread Execution
        
        Starts a new thread to run the check_update method
        """
        from threading import Thread

        thread = Thread(target=self.check_update)
        thread.start()
        ThreadProgress(thread, self.translate('processing'), '')

    def check_update(self):
        """Check update
        
        Checks for platformio updates each 5 days.
        To know what is the last version of platformio
        pypi is checked
        """
        installed = get_sysetting('installed', False)

        if(not installed):
            return

        from datetime import datetime, timedelta

        date_now = datetime.now()
        date_update = get_sysetting('last_check_update', False)

        try:
            date_update = datetime.strptime(date_update, '%Y-%m-%d %H:%M:%S.%f')

            if(date_now < date_update):
                return
        except:
            pass

        if(not date_update or date_now > date_update):
            date_update = date_now + timedelta(5, 0) # 5 días
            save_sysetting('last_check_update', str(date_update))

        from ..libraries.tools import get_headers
        from urllib.request import Request
        from urllib.request import urlopen
        from json import loads
        from re import sub

        self.realtime = False
        cmd = ['--version']
        out = run_command(cmd, prepare=True)

        pio_version = out[1]
        pio_version_int = int(sub(r'\D', '', pio_version))

        try:
            url = 'https://pypi.python.org/pypi/platformio/json'
            req = Request(url, headers=get_headers())
            response = urlopen(req)
            pypi_list = loads(response.read().decode())
            last_pio_version = pypi_list['info']['version']
            last_pio_version_int = int(sub(r'\D', '', last_pio_version))
        except:
            return

        if(pio_version_int < last_pio_version_int):
            from sublime import ok_cancel_dialog

            update = ok_cancel_dialog(self.translate('new_pio_update{0}{1}',
                last_pio_version,
                pio_version),
                self.translate('update_button'))

            if(update):
                self.show_feedback()
                self.realtime = True

                cmd = ['upgrade']
                out = run_command(cmd, prepare=True)
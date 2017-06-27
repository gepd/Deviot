#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

from .command import Command
from ..libraries import __version__ as version
from ..libraries.tools import create_command, get_setting
from ..libraries.messages import MessageQueue
from ..libraries.thread_progress import ThreadProgress
from ..libraries.I18n import I18n

_ = I18n

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
        global _
        
        _ = I18n().translate

        messages = MessageQueue("_deviot_starting{0}", version)
        messages.start_print()
        
        self.cwd = None
        self.dprint = messages.put
        self.derror = messages.print_once
        self.dstop = messages.stop_print

    def update_pio(self):
        """Update PlatformIO
        
        Update platformIO to the last version (block thread)
        """
        cmd = ['pio','upgrade']
        out = self.run_command(cmd, prepare=False)

    def update_async(self):
        """New Thread Execution
        
        Starts a new thread to run the update_pio method
        """
        from threading import Thread

        thread = Thread(target=self.update_pio)
        thread.start()
        ThreadProgress(thread, _('processing'), '')

    def developer_async(self):
        """New Thread Execution
        
        Starts a new thread to run the developer_pio method
        """
        from threading import Thread

        thread = Thread(target=self.developer_pio)
        thread.start()
        ThreadProgress(thread, _('processing'), '')

    def developer_pio(self):
        """Developer
        
        Uninstall the current version of platformio and install
        a version based in the preference of the user, it can be
        the stable or developer version
        """
        cmd = ['pip','uninstall', '--yes','platformio']
        out = self.run_command(cmd, prepare=False)

        if(get_setting('pio_developer', False)):
            option = 'https://github.com/platformio/' \
            'platformio/archive/develop.zip'
        else:
            option = 'platformio'

        cmd = ['pip','install', '-U', option]
        out = self.run_command(cmd, prepare=False)
# !/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import time
import sublime
from datetime import timedelta
from datetime import datetime

from Deviot.libraries import message
from Deviot.libraries import tools
from . import pio_handle


class Requirements(object):
    """
    Check the requirements of the plugin and install any dependency
    if it's necessary
    """

    def __init__(self):
        pass

    def check(self):
        """
        Checks the requirements to make deviot work
        """
        R_STATE = pio_handle.get_pio_install_state()

        # check for updates
        if(R_STATE == 200):
            self.check_updates()

        # install PlatformIO
        if(R_STATE == 103):
            self.pio_requests()

        # show error in cosole
        message.print_error(R_STATE)

    def pio_requests():
        """
        Checks the requirements to install PlatformIO
        as python. If PlatformIO is already installed it
        skip this step.
        """
        # check python
        from .python_install import check_python
        R_STATE = check_python()

        # check PlatformIO
        if(R_STATE is 200):
            R_STATE = pio_handle.check_pio()

        # Install pio
        if(R_STATE != 200):
            R_STATE = pio_handle.install()

        # set pio as installed
        if(R_STATE == 200):
            pio_handle.set_pio_installed()

    def check_updates():
        """
        check updates each x time defined in timedelta(5, 0)
        where 5 is 5 days
        """
        date_now = datetime.now()
        date_updt = tools.getConfig('check_update', False)

        # compare the dates to check updates
        try:
            date_updt = datetime.strptime(
                date_updt, '%Y-%m-%d %H:%M:%S.%f')

            if(date_now < date_updt):
                return
        except:
            return

        # saves the date in the config file for next check
        if(not date_updt or date_now > date_updt):
            date_updt = datetime.now() + timedelta(5, 0)
            tools.saveConfig('check_update', str(date_updt))

        # check for an update
        R_STATE = pio_handle.check_update()

        # update pio
        if(R_STATE == 104):
            R_STATE = pio_handle.install_command()

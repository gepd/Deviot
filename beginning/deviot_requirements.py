# !/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

from Deviot.libraries import message
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
        R_STATE = 200

        # Python and PlatformIO Check
        if(pio_handle.get_pio_install_state() != 200):
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
            if(R_STATE is 200):
                pio_handle.set_pio_installed()

        # print(pio_handle.check_upgrade())

        # show error
        message.print_error(R_STATE)

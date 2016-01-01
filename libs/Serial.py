#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import time
import glob
import threading

try:
    from . import Tools
except:
    from libs import Tools

if Tools.getOsName() == 'windows':
    if Tools.getPythonVersion() < 3:
        import _winreg as winreg
    else:
        import winreg


@Tools.singleton
class SerialListener(object):

    def __init__(self, func=None):
        self.func = func
        self.serial_list = []
        self.is_alive = False

    def start(self):
        if not self.is_alive:
            self.is_alive = True
            listener_thread = threading.Thread(target=self.update)
            listener_thread.start()

    def update(self):
        while self.is_alive:
            pre_serial_list = self.serial_list
            self.serial_list = listSerialPorts()
            if self.serial_list != pre_serial_list:
                if self.func:
                    self.func()
            time.sleep(1)

    def stop(self):
        self.is_alive = False


def listSerialPorts():
    os_name = Tools.getOsName()
    if os_name == "windows":
        serial_ports = listWinSerialPorts()
    elif os_name == 'osx':
        serial_ports = listOsxSerialPorts()
    else:
        serial_ports = listLinuxSerialPorts()
    serial_ports.sort()
    return serial_ports


def listWinSerialPorts():
    serial_ports = []
    has_ports = False
    path = 'HARDWARE\\DEVICEMAP\\SERIALCOMM'
    try:
        reg = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path,)
        has_ports = True
    except WindowsError:
        pass
    if has_ports:
        for i in range(128):
            try:
                name, value, type = winreg.EnumValue(reg, i)
            except WindowsError:
                pass
            else:
                serial_ports.append(value)
    return serial_ports


def listOsxSerialPorts():
    serial_ports = []
    dev_path = '/dev/'
    dev_names = ['tty.*', 'cu.*']
    for dev_name in dev_names:
        pattern = dev_path + dev_name
        serial_ports += glob.glob(pattern)
    return serial_ports


def listLinuxSerialPorts():
    serial_ports = []
    dev_path = '/dev/'
    dev_names = ['ttyACM*', 'ttyUSB*']
    for dev_name in dev_names:
        pattern = dev_path + dev_name
        serial_ports += glob.glob(pattern)
    return serial_ports

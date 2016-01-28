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
    from . import pyserial
    from . import Messages
    from .Preferences import Preferences
except:
    from libs import Tools
    from libs import pyserial
    from libs import Messages
    from libs.Preferences import Preferences

if Tools.getOsName() == 'windows':
    if Tools.getPythonVersion() < 3:
        import _winreg as winreg
    else:
        import winreg


@Tools.singleton
class SerialListener(object):
    """
    Constantly checks if a port has been connected or disconnected
    """

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


serials_in_use = []
serial_monitor_dict = {}


class SerialMonitor(object):
    """
    Handle the messages sended and received from/to the serial monitor
    """

    def __init__(self, serial_port, console=None):
        super(SerialMonitor, self).__init__()
        self.port = serial_port
        self.serial = pyserial.Serial()
        self.serial.port = serial_port
        self.queue = Messages.MessageQueue(console)
        self.Preferences = Preferences()
        self.is_alive = False

    def isRunning(self):
        return self.is_alive

    def start(self):
        self.queue.startPrint()
        if not self.is_alive:
            baudrate = self.Preferences.get('baudrate', 9600)
            self.serial.baudrate = baudrate
            if isSerialAvailable(self.port):
                self.serial.open()
                self.is_alive = True
                monitor_thread = threading.Thread(target=self.receive)
                monitor_thread.start()
            else:
                msg = 'Serial port {0} already in use. '
                msg += 'Try stopping any programs that may be using it.\\n'
                self.queue.put(msg, self.port)
                self.stop()

    def stop(self):
        self.is_alive = False
        self.queue.stopPrint()

    def receive(self):
        length_before = 0
        while self.is_alive:
            number = self.serial.inWaiting()
            if number > 0:
                in_text = self.serial.read(number)
                length_in_text = len(in_text)
                in_text = convertMode(in_text, length_before)
                self.queue.put(in_text)
                length_before += length_in_text
                length_before %= 16
            time.sleep(0.01)
        self.serial.close()

    def send(self, out_text):
        line_ending = self.Preferences.get('line_ending', '\n')
        out_text += line_ending
        self.queue.put('\\n[SENDED] {0}\\n', out_text)
        out_text = out_text.encode('utf-8', 'replace')
        self.serial.write(out_text)


def convertMode(in_text, str_len=0):
    """
    Convert a text in differents formats (ASCII,HEX)

    Arguments:
        in_text {string}
            Text to convert

    Keyword Arguments:
        str_len {int}
            leng of the in_text string (default: {0})

    Returns:
        [string] -- Converted string
    """
    text = u''
    display_mode = Preferences().get('display_mode', 'Text')
    if display_mode == 'Ascii':
        for character in in_text:
            text += chr(character)
    elif display_mode == 'Hex':
        for (index, character) in enumerate(in_text):
            text += u'%02X ' % character
            if (index + str_len + 1) % 8 == 0:
                text += '\t'
            if (index + str_len + 1) % 16 == 0:
                text += '\n'
    else:
        text = in_text.decode('utf-8', 'replace')
        text = text.replace('\r', '').replace('NULL', '')
    return text


def isSerialAvailable(serial_port):
    """
    Check if the serial port is available

    Arguments:
        serial_port {string}
            name of the port to check

    Returns:
        [bool] -- true or false when the port is available or not
    """
    state = False
    serial = pyserial.Serial()
    serial.port = serial_port
    try:
        serial.open()
    except pyserial.serialutil.SerialException:
        pass
    except UnicodeDecodeError:
        pass
    else:
        if serial.isOpen():
            state = True
            serial.close()
    return state


def listSerialPorts():
    """
    List all the serial ports availables in the diffents O.S
    """
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
    """
    List all the serial ports availables in Windows
    """
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
    """
    List all the serial ports availables in OS X
    """
    serial_ports = []
    dev_path = '/dev/'
    dev_names = ['tty.*', 'cu.*']
    for dev_name in dev_names:
        pattern = dev_path + dev_name
        serial_ports += glob.glob(pattern)
    return serial_ports


def listLinuxSerialPorts():
    """
    List all the serial ports availables in Linux
    """
    serial_ports = []
    dev_path = '/dev/'
    dev_names = ['ttyACM*', 'ttyUSB*']
    for dev_name in dev_names:
        pattern = dev_path + dev_name
        serial_ports += glob.glob(pattern)
    return serial_ports

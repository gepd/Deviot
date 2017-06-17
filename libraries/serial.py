#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals


from threading import Thread
from time import sleep

from . import __version__ as version
from ..libraries.pyserial.tools import list_ports
from ..libraries import pyserial
from .tools import get_setting
from .messages import MessageQueue
from .I18n import I18n

def serial_port_list():
    """List of Ports
    
    Return the list of serial ports availables on the system.
    
    Returns:
        [list/list] -- list of list like [['port1 fullname', 
                       port_name]['port2 fullname', 'port_name']]
    """
    ports = list(list_ports.comports()) 
    
    serial_ports = []
    for port_no, description, address in ports:
        serial_ports.append([description, port_no])

    return serial_ports


serials_in_use = []
serial_monitor_dict = {}


class SerialMonitor(object):
    """
    Handle the messages sended and received from/to the serial monitor
    """

    def __init__(self, serial_port):
        self.port = serial_port
        self.serial = pyserial.Serial()
        self.serial.port = serial_port
        self.is_alive = False
        self.baudrate = get_setting('baudrate', 9600)

        serial_header = I18n().translate("serial_monitor_header{0}{1}", version, serial_port)
        type_console = get_setting('type_console', 'exec')
        
        if('exec' not in type_console):
            type_console = serial_header.strip('\\n')
    
        message = MessageQueue(serial_header)
        message.set_console(type_console)
        message.start_print()

        self.dprint = message.put
        self.dstop = message.stop_print

    def is_running(self):
        """Monitor Running
        
        Check if the monitorserial is running
        
        Returns:
            [bool] -- True if it's running
        """
        return self.is_alive

    def start(self):
        """Start serial monitor
        
        Starts to receive data from the serial monitor in a new thread.

        """
        if(not self.is_alive):
            self.serial.baudrate = self.baudrate
            
            if is_available(self.port):
                self.serial.open()
                self.is_alive = True
                
                monitor_thread = Thread(target=self.receive)
                monitor_thread.start()
            else:
                self.stop()

    def stop(self):
        """Stop serial monitor
        
        Stops the loop who is wating for more information from the serial port
        """
        self.is_alive = False
        self.dstop()

    def receive(self):
        """Receive Data
        
        The loops will run until is_alive is true. After receive the serial data
        it can be converted to the mode selected by the user (ascii, hex, etc)
        """
        length_before = 0

        while self.is_alive:
            try:
                buf_number = self.serial.inWaiting()
            except:
                self.stop()

            if(buf_number > 0):
                inp_text = self.serial.read(buf_number)
                length_in_text = len(inp_text)
                inp_text = display_mode(inp_text, length_before)
                
                self.dprint(inp_text, hide_hour=True)
                
                length_before += length_in_text
                length_before %= 16
            
            sleep(0.04)
        
        self.serial.close()

    def send(self, out_text):
        """Send text
        
        Sends text over the serial port open, it adds a line ending
        according to the user preference.
        
        Arguments:
            out_text {str} -- text to send with the line ending
        """
        line_ending = self.Preferences.get('line_ending', '\n')
        out_text += line_ending
        out_text = out_text.encode('utf-8', 'replace')
        
        self.serial.write(out_text)


def is_available(serial_port):
    """Port available
    
    Checks if the serial port is available.

    Arguments:
        serial_port {str} -- Port name to check

    Returns:
        [bool] -- True when the port is available False if not
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

def display_mode(inp_text, str_len=0):
    """
    Convert a text in differents formats (ASCII,HEX)

    Arguments:
        inp_text {string}
            Text to convert

    Keyword Arguments:
        str_len {int}
            leng of the inp_text string (default: {0})

    Returns:
        [string] -- Converted string
    """
    text = u''
    display_mode = 'Text'
    
    if display_mode == 'Ascii':
        for character in inp_text:
            text += chr(character)
    
    elif display_mode == 'Hex':
        for (index, character) in enumerate(inp_text):
            text += u'%02X ' % character
            if (index + str_len + 1) % 8 == 0:
                text += '\t'
            if (index + str_len + 1) % 16 == 0:
                text += '\n'
    
    elif display_mode == 'Mix':
        text_mix = u''
        for (index, character) in enumerate(inp_text):
            text_mix += chr(character)
            text += u'%02X ' % character
            
            if (index + str_len + 1) % 8 == 0:
                text += '\t'
            
            if (index + str_len + 1) % 16 == 0:
                text_mix = text_mix.replace('\n', '+')
                text += text_mix
                text += '\n'
                text_mix = ''
        
        if(text_mix):
            less = (31 - index)
            for sp in range(less):
                text += '   '
            text += '\t'
            text += text_mix

    else:
        text = inp_text.decode('utf-8', 'replace')
        text = text.replace('\r', '').replace('NULL', '')
    
    return text


def toggle_serial_monitor():
    """Open/Close serial monitor
    
    If the serial monitor is closed, it will be opened or the opposite.
    """
    serial_monitor = None
    ports_list = serial_port_list()
    port_id = get_setting('port_id', None)

    print(serials_in_use)

    match = port_id in (port[1] for port in ports_list)

    if(not match):
        message = MessageQueue("_deviot_{0}", version)
        message.start_print()
        message.put("serial_not_available")
        message.stop_print()
        return

    if(port_id in serials_in_use):
        serial_monitor = serial_monitor_dict.get(port_id, None)

    if(not serial_monitor):
        serial_monitor = SerialMonitor(port_id)

    if(not serial_monitor.is_running()):
        serial_monitor.start()

        if(port_id not in serials_in_use):
            serials_in_use.append(port_id)

        serial_monitor_dict[port_id] = serial_monitor
    
    else:
        serial_monitor.stop()
        serials_in_use.remove(port_id)
        del serial_monitor_dict[port_id]
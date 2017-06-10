#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

from ..libraries.pyserial.tools import list_ports

def serial_port_list():    
    ports = list(list_ports.comports()) 
    
    serial_ports = []
    for port_no, description, address in ports:
        serial_ports.append([description, port_no])

    return serial_ports
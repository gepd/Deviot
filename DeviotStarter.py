#!/usr/bin/env python
#-*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import os
import re
import sublime
import sublime_plugin

class DeviotListener(sublime_plugin.EventListener):
	def __init__(self):
		super(DeviotListener, self).__init__()
		pass
		
	def on_activated(self, view):
		pass
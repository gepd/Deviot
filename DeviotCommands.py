#!/usr/bin/env python
#-*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import os
import subprocess
import sublime


class CommandsPy(object):
	def __init__(self):
		super(CommandsPy, self).__init__()

	def runCommand(self, command, cwd=None):
		
		process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,universal_newlines=True,shell=True)
		output = process.communicate()[0]
		return output
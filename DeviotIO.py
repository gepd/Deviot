#!/usr/bin/env python
#-*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

from . import DeviotCommands
from . import DeviotFunctions
from . import DeviotPaths

class platformioCLI(DeviotCommands.CommandsPy):
	def __init__(self, view):
		self.Preferences = DeviotFunctions.Preferences()
		self.Commands = DeviotCommands.CommandsPy()
		self.currentFilePath = DeviotPaths.getCurrentFilePath(view)
		self.cwd = DeviotPaths.getCWD(self.currentFilePath)
		self.view = view

	def getSelectedBoards(self):		
		boards = self.Preferences.data['board_id']
		type_boards = ""

		for board in boards:
			type_boards += "--board=%s " % board

		return type_boards

	def initSketch(self):
		init_boards = self.getSelectedBoards()
		command = "platformio -f -c sublimetext init %s" % init_boards

		if(DeviotFunctions.isIOTFile(self.view)):
			self.Commands.runCommand(command, self.cwd)

	def buildSketch(self):
		self.initSketch()
		if(not self.Commands.error_running):
			pass

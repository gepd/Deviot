#!/usr/bin/env python
#-*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import json

from . import DeviotCommands
from . import DeviotFunctions
from . import DeviotPaths

class platformioCLI(DeviotCommands.CommandsPy):
	def __init__(self, view=False):
		self.Preferences = DeviotFunctions.Preferences()
		self.Commands = DeviotCommands.CommandsPy()		
		self.view = view
		if(view):
			self.currentFilePath = DeviotPaths.getCurrentFilePath(view)
			self.cwd = DeviotPaths.getCWD(self.currentFilePath)

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
			print("Initializing the project")
			self.Commands.runCommand(command, self.cwd)

	def buildSketch(self):
		self.getAPICOMPorts()
		return
		self.initSketch()
		if(not self.Commands.error_running and DeviotFunctions.isIOTFile(self.view)):
			command = "platformio -f -c sublimetext run"
			print("Building the project")
			self.Commands.runCommand(command, self.cwd)
			print("Finished")

	def getAPICOMPorts(self):
		command = "platformio serialports list --json-output"
		port_list = json.loads(self.Commands.runCommand(command,setReturn=True))

		if(not self.Commands.error_running):
			return port_list

	def getAPIBoards(self):
		"""Get boards list
		
		Get the boards list from the platformio API using CLI.
		to know more about platformio visit:  http://www.platformio.org/

		Returns: 
		 	{json object} -- list with all boards in a JSON format
		"""
		boards = []
		cmd = "platformio boards --json-output"
		boards = self.Command.runCommand(cmd,setReturn=True)
		return boards
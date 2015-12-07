#!/usr/bin/env python
#-*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import os
import threading
import subprocess
import sublime
import re
import time
import codecs
import json

from . import DeviotCommands
from . import DeviotPaths

# Handle JSON Files
class JSONFile(object):
	def __init__(self, path,encoding='utf-8'):		
		super(JSONFile, self).__init__()		
		self.setEncoding(encoding)		
		self.path = path
		self.loadFile()

	# load the data from a JSON File
	def loadFile(self):
		text = ''
		try:
			with open(self.path, 'r') as f:
				return f.read()
		except (IOError, UnicodeError):
			pass

	# Save a JSON File
	def saveJSONFile(self, text, append=False):		
		mode = 'w'
		if append:
			mode = 'a'
		try:
			with open(self.path, mode, self.encoding) as f:
				f.write(text)
		except (IOError, UnicodeError):
			pass

	# set the encoding for json files
	def setEncoding(self, encoding='utf-8'):
		self.encoding = encoding

# Initialization of the plugin menu

class Menu(object):
	def __init__(self,menu_dict=None):
		super(Menu, self).__init__()
		self.Command = DeviotCommands.CommandsPy()

	# get a json list of all boards availables from platformio
	def getWebBoards(self):
		boards = []
		cmd = "platformio boards --json-output"
		boards = self.Command.runCommand(cmd)
		return boards

	# Generate the Main menu
	def createMainMenu(self):
		#self.saveWebBoards()
		self.createBoardsMenu()
		return
		full = [{'caption':'uno','children':[{'caption':'dos'}]}]
		preset_path = DeviotPaths.getPresetPath()
		main_file_name = 'menu_main.json'
		main_file_path = os.path.join(preset_path,main_file_name)
		menu_file = JSONFile(main_file_path)
		menu_data = menu_file.data
		for menu in menu_data:
			for sub_menu in menu['children']:
				for key in sub_menu:
					value = sub_menu.get(key)
					if(sub_menu[key] == []):
						sub_menu[key] = full		

		deviot_user_path = DeviotPaths.getDeviotUserPath()
		if(not os.path.isdir(deviot_user_path)):
			os.makedirs(deviot_user_path)
		main_user_file_path = os.path.join(deviot_user_path, 'Main.sublime-menu')
		main_user_file_path = JSONFile(main_user_file_path)
		main_user_file_path.saveFile(menu_data)

	def saveWebBoards(self):
		boards = self.getWebBoards()
		file = JSONFile(DeviotPaths.getDeviotBoardsPath())
		file.saveJSONFile(boards)

	def getFileBoards(self):
		file = JSONFile(DeviotPaths.getDeviotBoardsPath())
		boards = file.loadFile()
		return boards

	def createBoardsMenu(self):
		list = []
		boards = json.loads(self.getFileBoards())
		
		for key,value in boards.items():
			list.append(key)
		print(list)

# Set the status in the status bar of ST
def setStatus(view):
	info = []
	exts = ['ino','pde','cpp','c','.S']
	file_name = view.file_name()

	if file_name and file_name.split('.')[-1] in exts:
		info.append('Deviot ' + getVersion())
		Fullinfo = ', '.join(info)

		view.set_status('Deviot', Fullinfo)

# get the current version of the plugin
def getVersion():
	return "0.1"
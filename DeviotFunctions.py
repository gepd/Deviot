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
		self.data = {}
		self.path = path
		self.loadData()

	# load the data from a JSON File
	def loadData(self):
		try:
			text = self.readFile()
		except:
			return
			
		try:
			self.data = json.loads(text)
		except:
			pass
	
	def setData(self, data):
		self.data = data
		self.saveData()

	# Save a JSON File
	def saveData(self):
		text = json.dumps(self.data, sort_keys=True, indent=4)
		self.writeFile(text)

	def readFile(self):
		text = ''

		try:
			with codecs.open(self.path, 'r', self.encoding) as file:
				text = file.read()
		except (IOError, UnicodeError):
			pass

		return text

	def writeFile(self, text, append=False):
		mode = 'w'

		if append:
			mode = 'a'
		try:
			with codecs.open(self.path, mode, self.encoding) as file:
				file.write(text)
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
		preferences_path = DeviotPaths.getPreferencesFile()
		self.Preferences = Preferences(preferences_path)

	# get a json list of all boards availables from platformio
	def getWebBoards(self):
		boards = []
		cmd = "platformio boards --json-output"
		boards = self.Command.runCommand(cmd)
		return boards

	def saveWebBoards(self):
		boards = self.getWebBoards()
		file = JSONFile(DeviotPaths.getDeviotBoardsPath())
		file.saveData(boards)

	def getFileBoards(self):
		file = JSONFile(DeviotPaths.getDeviotBoardsPath())
		boards = file.data
		return boards

	def createBoardsMenu(self):
		vendors = {}
		boards = []
		
		datas = self.getFileBoards()

		for datakey,datavalue in datas.items():					
			for infokey,infovalue in datavalue.items():
				vendor = datavalue['vendor']
				if(infokey == 'name'):
					name = infovalue.replace(vendor + " ","",1)
					children = vendors.setdefault(vendor,[])
					children.append({"caption":name,"id":infovalue.lower()})

		for vendor, children in vendors.items():
			boards.append({"caption":vendor,"children":children})

		boards = sorted(boards, key=lambda x:x['caption'])
		boards = json.dumps(boards)

		return boards

	# Generate the Main menu
	def createMainMenu(self):
		boards = json.loads(self.createBoardsMenu())
		preset_path = DeviotPaths.getPresetPath()
		main_file_name = 'menu_main.json'
		main_file_path = os.path.join(preset_path,main_file_name)
		menu_file = JSONFile(main_file_path)
		menu_data = menu_file.data[0]

		for fist_menu in menu_data:
			for second_menu in menu_data[fist_menu]:
				if 'children' in second_menu:
					second_menu['children'] = boards
		
		# to format purposes
		menu_data = [menu_data]

		deviot_user_path = DeviotPaths.getDeviotUserPath()
		if(not os.path.isdir(deviot_user_path)):
			os.makedirs(deviot_user_path)
		main_user_file_path = os.path.join(deviot_user_path, 'Main.sublime-menu')
		file_menu = JSONFile(main_user_file_path)
		file_menu.setData(menu_data)
		file_menu.saveData()

class Preferences(JSONFile):
	def __init__(self, path):
		super(Preferences, self).__init__(path)

	def set(self, key, value):
		self.data[key] = value
		self.saveData()

	def get(self, key, default_value=False):
		value = self.data.get(key, default_value)
		return value

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
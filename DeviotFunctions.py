#!/usr/bin/env python
#-*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import os
import sublime
import codecs
import json

from . import DeviotCommands
from . import DeviotPaths
from . import DeviotIO

class JSONFile(object):
	"""Handle JSON Files
	
	This class allow to load and save JSON files
	"""
	def __init__(self, path):
		"""JSONFile Construct
		
		This construct load a file when is called and
		load the information in a global variable
		
		Arguments:
			path {string} -- Full path of the JSON file
		"""
		super(JSONFile, self).__init__()		
		self.setEncoding()
		self.data = {}
		self.path = path
		self.loadData()		

	def loadData(self):
		"""Load JSON File
		
		Load the content of a JSON file and 
		deserialize it to set the information 
		in a global object called data
		"""
		try:
			text = self.readFile()
		except:
			return
			
		try:
			self.data = json.loads(text)
		except:
			pass
	
	def setData(self, data):
		"""Set the JSON data
		
		Save the data in the file setted on the
		construct. This method is most used in 
		the preferences class.
		
		Arguments:
			data {string} -- data to save in the JSON file.
		"""
		self.data = data
		self.saveData()

	def saveData(self):
		"""Save JSON data
		
		Serialize the data stored in the global object data
		and call to Write file. This function is called automatically
		when any data is set in the method SetData.
		
		"""
		text = json.dumps(self.data, sort_keys=True, indent=4)
		self.writeFile(text)

	def readFile(self):
		"""Read File
		
		Read the data from the file specified in the global object path.
		The data readed is encoded with the format specified in the global
		object encoding, by default this object is UTF-8. Use this method 
		if you don't want to modify the data received from the file.

		Returns:
			text {string} -- encoded text readed from file
		"""
		text = ''

		try:
			with codecs.open(self.path, 'r', self.encoding) as file:
				text = file.read()
		except (IOError, UnicodeError):
			pass

		return text

	def writeFile(self, text, append=False):
		"""Write File
		
		Write the data passed in a file specified in the global object path.
		This method is called automatically by saveData, and encode the text
		in the format specified in the global object encoding, by default this
		object is UTF-8. Use this method if you don't want to modify the data
		to write.
		
		Arguments:
			text {string} -- Text to write in the file
		
		Keyword Arguments:
			append {boolean} -- Set to True if you want to append the data in the file (default: False)
		"""
		mode = 'w'

		if append:
			mode = 'a'
		try:
			with codecs.open(self.path, mode, self.encoding) as file:
				file.write(text)
		except (IOError, UnicodeError):
			pass

	def setEncoding(self, encoding='utf-8'):
		"""Change encoding
		
		Call this method to change the format to encode the files when you 
		load it or save it.
		
		Keyword Arguments:
			encoding {string} -- Format to encoding (default: UTF-8 )
		"""
		self.encoding = encoding

class Menu(object):
	"""Plugin Menu
	
	Class to handle the differents option in the plugin menu.
	"""
	def __init__(self):
		"""Construct
		
		Call the construct of the command library to make the
		differents call by CLI
		"""
		super(Menu, self).__init__()
		self.Command = DeviotCommands.CommandsPy()

	def saveWebBoards(self):
		"""Save board list
		
		Save the JSON object in a specific JSON file
		"""
		boards = DeviotIO.platformioCLI().getAPIBoards()
		file = JSONFile(DeviotPaths.getDeviotBoardsPath())
		file.saveData(boards)

	def getFileBoards(self):
		"""Get Board File
		
		Load the board list stored in a JSON file and 
		return the data. This function is used to avoid
		always download the list from the web.

		Returns:
		 	{json object} -- list with all boards in a JSON format
		"""
		file = JSONFile(DeviotPaths.getDeviotBoardsPath())
		boards = file.data
		return boards

	def createBoardsMenu(self):
		"""Board menu
		
		Load the JSON file with the list of all boards and re order it
		based on the vendor. after that format the data to operate with
		the standards required for the ST

		Returns:
		  	{json array} -- list of all boards to show in the menu
		"""
		vendors = {}
		boards = []
		
		datas = self.getFileBoards()

		for datakey,datavalue in datas.items():
			for infokey,infovalue in datavalue.items():
				vendor = datavalue['vendor']
				if(infokey == 'name'):
					name = infovalue.replace(vendor + " ","",1)
					children = vendors.setdefault(vendor,[])
					children.append({"caption":name,'command':'select_board',"id":datakey,"checkbox":True,"args":{"board_id":datakey}})

		for vendor, children in vendors.items():
			boards.append({"caption":vendor,"children":children})

		boards = sorted(boards, key=lambda x:x['caption'])
		boards = json.dumps(boards)

		return boards

	def createSerialPortsMenu(self):
		"""Serial ports
		
		Create the list menu "Serial ports" with the list of all the
		availables serial ports
		"""
		port_list = DeviotIO.platformioCLI().getAPICOMPorts()
		menu_ports = []


		for port in port_list:
			port_name = port["port"]
			menu_ports.append({"caption":port_name,"id":port_name.lower()})

		return menu_ports

	def createMainMenu(self):
		"""Main menu
		
		Creates the main menu with the differents options
		including boards, libraries, COM ports, and user
		options.
		"""
		port_list = self.createSerialPortsMenu()

		boards = json.loads(self.createBoardsMenu())
		main_file_path = DeviotPaths.getMainJSONFile()
		menu_file = JSONFile(main_file_path)
		menu_data = menu_file.data[0]

		for fist_menu in menu_data:
			for second_menu in menu_data[fist_menu]:
				if 'children' in second_menu:
					if(second_menu['id'] == 'initialize'):
						#second_menu['children'] = boards
						pass
					if(second_menu['id'] == 'serial_ports'):
						#second_menu['children'] = port_list
						pass
		
		# to format purposes
		menu_data = [menu_data]
		
		main_user_file_path = DeviotPaths.getDeviotMenuPath()
		file_menu = JSONFile(main_user_file_path)
		file_menu.setData(menu_data)
		file_menu.saveData()


class Preferences(JSONFile):
	"""Preferences
	
	Class to handle the preferences of the plugin
	
	Extends:
		JSONFile
	"""
	def __init__(self):
		"""Construct
		
		Path loads the file where the preferences are stored,
		Doing that you avoid to pass the path every time you
		need to get or set any preference.
		"""
		path = DeviotPaths.getPreferencesFile()
		super(Preferences, self).__init__(path)

	def set(self, key, value):
		"""Set value
		
		Save a value in the preferences file using a list and
		dictionaries.
		
		Arguments:
			key {string} -- identifier of the preference
			value {[type]} -- value of the preference
		"""
		self.data[key] = value
		self.saveData()

	def get(self, key, default_value=False):
		"""Get Value
		
		Get a value in the preferences file stored as a list and
		dictionaries format.
		
		Arguments:
			key {string} -- identifier of the preference
		
		Keyword Arguments:
			default_value {string} -- if there is none value stored
									  you can set a default value (default: False)
		
		Returns:
		   	{string} -- Value of the preference
		"""
		value = self.data.get(key, default_value)
		return value

	def boardSelected(self,board_id):
		"""Choosed board
		
		Add or delete the board selected from the preferences
		files. The boards are formated in a dictionary in the
		the list 'board id'
		
		Arguments:
			board_id {string} -- identifier if the board selected
		"""
		fileData = self.data
		
		if(fileData):
			if board_id in fileData['board_id']:
				fileData.setdefault('board_id',[]).remove(board_id)
			else:
				fileData.setdefault('board_id',[]).append(board_id)
			
			self.data = fileData
			self.saveData()
		else:
			self.set('board_id',[board_id])


	def checkBoard(self, board_id):
		"""Is checked
		
		Check if is necessary to mark or unmark the board selected 
		
		Arguments:
			board_id {string]} -- identifier of the board selected
		"""
		check = False
		if(self.data):
			check_boards = self.get('board_id',board_id)

			if board_id in check_boards:
				check = True
		return check


def isIOTFile(view):
	"""IoT File
	
	Check if the file in the current view of ST is an allowed
	IoT file, the files are specified in the exts variable.
	
	Arguments:
		view {st object} -- stores many info related with ST
	"""
	exts = ['ino','pde','cpp','c','.S']
	file_name = view.file_name()

	if file_name and file_name.split('.')[-1] in exts:
		return True
	return False

def setStatus(view):
	"""Status bar
	
	Set the info to show in the status bar of Sublime Text.
	This info is showing only when the working file is considered IoT
	
	Arguments:
		view {st object} -- stores many info related with ST
	"""
	info = []

	if isIOTFile(view):		
		info.append('Deviot ' + getVersion())
		full_info = " | ".join(info)

		view.set_status('Deviot', full_info)

def getVersion():
	"""Plugin Version
	
	Get the current version of the plugin stored in the preferences file.

	Returns:
	  	{String} -- Version of the file (only numbers)
	"""
	return Preferences().get('plugin_version')

def setVersion(version):
	"""Plugin Version
	
	Save the current version of the plugin in the preferences file.

	Returns:
	  	{String} -- Version of the file (only numbers)
	 """
	Preferences().set('plugin_version',version)
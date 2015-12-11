#!/usr/bin/env python
#-*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import sublime, sublime_plugin

from . import DeviotFunctions
from . import DeviotPaths

class DeviotListener(sublime_plugin.EventListener):
	"""Starter class
	
	This is the first class to run when the plugin is excecuted
	
	Extends:
		sublime_plugin.EventListener
	"""
	def __init__(self):
		""" Constructor
		
		In this constructor is setted the version of the 
		plugin, and running the creation of the differents
		menus located in the top of sublime text
		"""
		super(DeviotListener, self).__init__()
		DeviotFunctions.Menu().createMainMenu()
		DeviotFunctions.setVersion('0.5')

	def on_activated(self, view):
		"""Activated view
		
		When any tab is activated, this fuction runs.
		From here the plugin detects if the current
		tab is working with any file allowed to working
		with this plugin
		
		Arguments:
			view {st object} -- stores many info related with ST
		"""
		DeviotFunctions.setStatus(view)

		
class UpdateMenuCommand(sublime_plugin.WindowCommand):
	"""Update/refresh menu
	
	This command updates the main menu including the list of boards 
	vendors/type of board.
	
	Extends:
		sublime_plugin.WindowCommand
	"""
	def run(self):
		DeviotFunctions.Menu().createMainMenu()

class SelectBoardCommand(sublime_plugin.WindowCommand):
	"""Select Board Trigger
	
	This class trigger two methods to know what board(s)
	were chosen and to store it in a preference file.
	
	Extends:
		sublime_plugin.WindowCommand
	"""
	def run(self,board_id):
		"""ST method
		
		Get the ID of the board selected and store it in a
		preference file.
		
		Arguments:
			board_id {string} -- id of the board selected
		"""
		DeviotFunctions.Preferences().boardSelected(board_id)

	def is_checked(self,board_id):
		"""ST method
		
		Check if the node in the menu is check or not, this
		function need to return always a bolean
		
		Arguments:
			board_id {string} -- id of the board selected
		"""
		check = DeviotFunctions.Preferences().checkBoard(board_id)
		return check

class BuildSketchCommand(sublime_plugin.WindowCommand):
	"""Build Sketch Trigger
	
	This class trigger one method to build the files in the
	current working project
	
	Extends:
		sublime_plugin.WindowCommand
	"""
	def run(self,edit):
		"""ST method
		
		Call a method to build an accepted IoT File
		
		Arguments:
			edit {object} -- ST object
		"""
		DeviotFunctions.PlatformioCLI(self.view).buildSketch()

class SelectPortCommand(sublime_plugin.WindowCommand):
	"""Select port
	
	Save in the preferences file, the port com to upload the sketch
	when the upload command is use
	
	Extends:
		sublime_plugin.WindowCommand
	"""
	def run(self, id_port):
		DeviotFunctions.Preferences().set('id_port',id_port)
	def is_checked(self,id_port):
		saved_id_port = DeviotFunctions.Preferences().get('id_port')
		return saved_id_port == id_port
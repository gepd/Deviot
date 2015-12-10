#!/usr/bin/env python
#-*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import sublime, sublime_plugin

from . import DeviotFunctions
from . import DeviotPaths
from . import DeviotIO

class DeviotListener(sublime_plugin.EventListener):
	def __init__(self):
		super(DeviotListener, self).__init__()
		DeviotFunctions.Menu().createMainMenu()
		DeviotFunctions.setVersion('0.5')	
		
	def on_activated(self, view):
		DeviotFunctions.setStatus(view)

class UpdateMenuCommand(sublime_plugin.WindowCommand):
	def run(self,id):
		pass

class SelectBoardCommand(sublime_plugin.WindowCommand):
	def run(self,board_id):		
		DeviotFunctions.Preferences().selectBoard(board_id)

	def is_checked(self,board_id):
		check = DeviotFunctions.Preferences().checkBoard(board_id)
		return check

class BuildSketchCommand(sublime_plugin.TextCommand):
	def run(self,edit):
		DeviotIO.platformioCLI(self.view).buildSketch()

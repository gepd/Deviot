import os
import sublime
import sublime_plugin

from ..libraries.menu import Menu


class SelectBoardCommand(sublime_plugin.WindowCommand):

    def run(self):
        Menu().boards_menu()

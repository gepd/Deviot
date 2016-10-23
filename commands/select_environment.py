import os
import sublime
import sublime_plugin

from ..libraries.menu import Menu


class SelectEnvironmentCommand(sublime_plugin.WindowCommand):

    def run(self):
        Menu().environment_menu()

# !/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import sublime
import sublime_plugin
import threading

from .commands import *
from .beginning.deviot_requirements import Requirements


def plugin_loaded():
    window = sublime.active_window()

    thread = threading.Thread(target=Requirements().check())
    thread.start()

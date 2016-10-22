#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import sublime

quick_panel_active = False
quick_panel_id = 0


def quick_panel(items, callback, window=False, flags=0, index=0):
    if(not flags):
        flags = sublime.KEEP_OPEN_ON_FOCUS_LOST
    window = sublime.active_window()
    window.show_quick_panel(items, callback, flags, index)

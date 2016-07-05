#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

quick_panel_active = False
quick_panel_id = 0


def quickPanel(w, items, callback, flags=0, index=0):
    w.show_quick_panel(items, callback, flags, index)

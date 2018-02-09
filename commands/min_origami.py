# The MIT License (MIT)

# Copyright (c) 2017 Origami Contributors

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# This file has been took from https://github.com/SublimeText/Origami and
# modified to work with this plugin

from __future__ import division
import sublime
import sublime_plugin
import copy
from functools import partial

XMIN, YMIN, XMAX, YMAX = list(range(4))


def increment_if_greater_or_equal(x, threshold):
    if x >= threshold:
        return x+1
    return x


def decrement_if_greater(x, threshold):
    if x > threshold:
        return x-1
    return x


def pull_up_cells_after(cells, threshold):
    return [[x0, decrement_if_greater(y0, threshold),
             x1, decrement_if_greater(y1, threshold)]
            for (x0, y0, x1, y1) in cells]


def push_right_cells_after(cells, threshold):
    return [[increment_if_greater_or_equal(x0, threshold), y0,
             increment_if_greater_or_equal(x1, threshold), y1]
            for (x0, y0, x1, y1) in cells]


def push_down_cells_after(cells, threshold):
    return [[x0, increment_if_greater_or_equal(y0, threshold),
             x1, increment_if_greater_or_equal(y1, threshold)]
            for (x0, y0, x1, y1) in cells]


def pull_left_cells_after(cells, threshold):
    return [[decrement_if_greater(x0, threshold), y0,
             decrement_if_greater(x1, threshold), y1]
            for (x0, y0, x1, y1) in cells]


def opposite_direction(direction):
    opposites = {"up": "down", "right": "left", "down": "up", "left": "right"}
    return opposites[direction]


def cells_adjacent_to_cell_in_direction(cells, cell, direction):
    fn = None
    if direction == "up":
        fn = lambda orig, check: orig[YMIN] == check[YMAX]
    elif direction == "right":
        fn = lambda orig, check: orig[XMAX] == check[XMIN]
    elif direction == "down":
        fn = lambda orig, check: orig[YMAX] == check[YMIN]
    elif direction == "left":
        fn = lambda orig, check: orig[XMIN] == check[XMAX]

    if fn:
        return [c for c in cells if fn(cell, c)]
    return None


def fixed_set_layout(window, layout):
    # A bug was introduced in Sublime Text 3, sometime before 3053, in that it
    # changes the active group to 0 when the layout is changed. Annoying.
    active_group = window.active_group()
    window.set_layout(layout)
    num_groups = len(layout['cells'])
    window.focus_group(min(active_group, num_groups-1))


def fixed_set_layout_no_focus_change(window, layout):
    active_group = window.active_group()
    window.set_layout(layout)


class WithSettings:
    _settings = None

    def settings(self):
        if self._settings is None:
            self._settings = sublime.load_settings('Origami.sublime-settings')
        return self._settings


class PaneCommand(sublime_plugin.WindowCommand):
    "Abstract base class for commands."

    def get_layout(self):
        layout = self.window.get_layout()
        cells = layout["cells"]
        rows = layout["rows"]
        cols = layout["cols"]
        return rows, cols, cells

    def get_cells(self):
        return self.get_layout()[2]

    def adjacent_cell(self, direction):
        cells = self.get_cells()
        current_cell = cells[self.window.active_group()]
        adjacent_cells = cells_adjacent_to_cell_in_direction(
            cells, current_cell, direction)
        rows, cols, _ = self.get_layout()

        if direction in ["left", "right"]:
            MIN, MAX, fields = YMIN, YMAX, rows
        else:  # up or down
            MIN, MAX, fields = XMIN, XMAX, cols

        cell_overlap = []
        for cell in adjacent_cells:
            start = max(fields[cell[MIN]], fields[current_cell[MIN]])
            end = min(fields[cell[MAX]], fields[current_cell[MAX]])
            # / (fields[cell[MAX]] - fields[cell[MIN]])
            overlap = (end - start)
            cell_overlap.append(overlap)

        if len(cell_overlap) != 0:
            cell_index = cell_overlap.index(max(cell_overlap))
            return adjacent_cells[cell_index]
        return None

    def duplicated_views(self, original_group, duplicating_group):
        original_views = self.window.views_in_group(original_group)
        original_buffers = [v.buffer_id() for v in original_views]
        potential_dupe_views = self.window.views_in_group(duplicating_group)
        dupe_views = []
        for pd in potential_dupe_views:
            if pd.buffer_id() in original_buffers:
                dupe_views.append(pd)
        return dupe_views

    def travel_to_pane(self, direction, create_new_if_necessary=False):
        adjacent_cell = self.adjacent_cell(direction)
        if adjacent_cell:
            cells = self.get_cells()
            new_group_index = cells.index(adjacent_cell)
            self.window.focus_group(new_group_index)
        elif create_new_if_necessary:
            self.create_pane(direction, True)

    def create_pane(self, direction, give_focus=False):
        window = self.window
        rows, cols, cells = self.get_layout()
        current_group = window.active_group()

        old_cell = cells.pop(current_group)
        new_cell = []

        if direction in ("up", "down"):
            cells = push_down_cells_after(cells, old_cell[YMAX])
            rows.insert(old_cell[YMAX], (rows[old_cell[YMIN]] +
                                         rows[old_cell[YMAX]]) / 2)
            new_cell = [old_cell[XMIN], old_cell[YMAX],
                        old_cell[XMAX], old_cell[YMAX]+1]
            old_cell = [old_cell[XMIN], old_cell[
                YMIN], old_cell[XMAX], old_cell[YMAX]]

        elif direction in ("right", "left"):
            cells = push_right_cells_after(cells, old_cell[XMAX])
            cols.insert(
                old_cell[XMAX], (cols[old_cell[XMIN]] +
                                 cols[old_cell[XMAX]]) / 2)
            new_cell = [old_cell[XMAX], old_cell[YMIN],
                        old_cell[XMAX]+1, old_cell[YMAX]]
            old_cell = [old_cell[XMIN], old_cell[
                YMIN], old_cell[XMAX], old_cell[YMAX]]

        if new_cell:
            if direction in ("left", "up"):
                focused_cell = new_cell
                unfocused_cell = old_cell
            else:
                focused_cell = old_cell
                unfocused_cell = new_cell
            cells.insert(current_group, focused_cell)
            cells.append(unfocused_cell)
            layout = {"cols": cols, "rows": rows, "cells": cells}
            fixed_set_layout(window, layout)

            if give_focus:
                self.travel_to_pane(direction)

    def destroy_current_pane(self):
        # Out of the four adjacent panes, one was split to create this pane.
        # Find out which one, move to it, then destroy this pane.
        cells = self.get_cells()

        current = cells[self.window.active_group()]
        choices = {}
        choices["up"] = self.adjacent_cell("up")
        choices["right"] = self.adjacent_cell("right")
        choices["down"] = self.adjacent_cell("down")
        choices["left"] = self.adjacent_cell("left")

        target_dir = None
        for dir, c in choices.items():
            if not c:
                continue
            if dir in ["up", "down"]:
                if c[XMIN] == current[XMIN] and c[XMAX] == current[XMAX]:
                    target_dir = dir
            elif dir in ["left", "right"]:
                if c[YMIN] == current[YMIN] and c[YMAX] == current[YMAX]:
                    target_dir = dir
        if target_dir:
            self.travel_to_pane(target_dir)
            self.destroy_pane(opposite_direction(target_dir))


class DeviotCreatePaneCommand(PaneCommand):

    def run(self, direction, give_focus=False):
        self.create_pane(direction, give_focus)

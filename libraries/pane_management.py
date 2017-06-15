from __future__ import division
import sublime, sublime_plugin

XMIN, YMIN, XMAX, YMAX = list(range(4))

def increment_if_greater_or_equal(x, threshold):
    if x >= threshold:
        return x+1
    return x

def push_down_cells_after(cells, threshold):
    return [    [x0,increment_if_greater_or_equal(y0, threshold),
                x1,increment_if_greater_or_equal(y1, threshold)] for (x0,y0,x1,y1) in cells]

def fixed_set_layout(window, layout):
    #A bug was introduced in Sublime Text 3, sometime before 3053, in that it
    #changes the active group to 0 when the layout is changed. Annoying.
    active_group = window.active_group()
    window.set_layout(layout)
    num_groups = len(layout['cells'])
    window.focus_group(min(active_group, num_groups-1))

def cells_adjacent_to_cell_in_direction(cells, cell, direction):
    fn = None
    if direction == "down":
        fn = lambda orig, check: orig[YMAX] == check[YMIN]

    if fn:
        return [c for c in cells if fn(cell, c)]
    return None

def opposite_direction(direction):
    opposites = {"down":"up"}
    return opposites[direction]

class DeviotPaneCommand(sublime_plugin.WindowCommand):
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
        adjacent_cells = cells_adjacent_to_cell_in_direction(cells, current_cell, direction)
        rows, cols, _ = self.get_layout()

        if direction in ["left", "right"]:
            MIN, MAX, fields = YMIN, YMAX, rows
        else: #up or down
            MIN, MAX, fields = XMIN, XMAX, cols

        cell_overlap = []
        for cell in adjacent_cells:
            start = max(fields[cell[MIN]], fields[current_cell[MIN]])
            end = min(fields[cell[MAX]], fields[current_cell[MAX]])
            overlap = (end - start)# / (fields[cell[MAX]] - fields[cell[MIN]])
            cell_overlap.append(overlap)

        if len(cell_overlap) != 0:
            cell_index = cell_overlap.index(max(cell_overlap))
            return adjacent_cells[cell_index]
        return None

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
            rows.insert(old_cell[YMAX], (rows[old_cell[YMIN]] + rows[old_cell[YMAX]]) / 2)
            new_cell = [old_cell[XMIN], old_cell[YMAX], old_cell[XMAX], old_cell[YMAX]+1]
            old_cell = [old_cell[XMIN], old_cell[YMIN], old_cell[XMAX], old_cell[YMAX]]

        if new_cell:
            focused_cell = old_cell
            unfocused_cell = new_cell
            cells.insert(current_group, focused_cell)
            cells.append(unfocused_cell)
            layout = {"cols": cols, "rows": rows, "cells": cells}
            fixed_set_layout(window, layout)

            if give_focus:
                self.travel_to_pane(direction)

    def destroy_current_pane(self):
        #Out of the four adjacent panes, one was split to create this pane.
        #Find out which one, move to it, then destroy this pane.
        cells = self.get_cells()

        current = cells[self.window.active_group()]
        choices = {}
        choices["down"] = self.adjacent_cell("down")

        target_dir = None
        for dir,c in choices.items():
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

    def destroy_pane(self, direction):
        if direction == "self":
            self.destroy_current_pane()
            return

    def travel_to_pane(self, direction, create_new_if_necessary=False):
        adjacent_cell = self.adjacent_cell(direction)
        if adjacent_cell:
            cells = self.get_cells()
            new_group_index = cells.index(adjacent_cell)
            self.window.focus_group(new_group_index)
        elif create_new_if_necessary:
            self.create_pane(direction, True)

class DeviotCreatePaneCommand(DeviotPaneCommand):
    def run(self, direction, give_focus=False):
        self.create_pane(direction, give_focus)

class DeviotDestroyPaneCommand(DeviotPaneCommand):
    def run(self, direction):
        print("destroy: ", direction)
        self.destroy_pane(direction)
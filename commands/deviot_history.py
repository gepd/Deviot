"""
Copyright (c) 2015 Randy Lai <randy.cs.lai@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from sublime import Region
from sublime_plugin import TextCommand


class History:
    hist = []
    index = None

    def insert(self, user_input):
        if not self.hist or (user_input != self.last() and user_input != "last_regex"):
            self.hist.append(user_input)
            self.index = None

    def roll(self, backwards=False):
        if self.index is None:
            self.index = -1 if backwards else 0
        else:
            self.index += -1 if backwards else 1

        if self.index == len(self.hist) or self.index < -len(self.hist):
            self.index = -1 if backwards else 0

    def last(self):
        return self.hist[-1] if self.hist else None

    def get(self, index=None):
        if not index:
            index = self.index
        return self.hist[index] if self.hist else None

    def reset_index(self):
        self.index = None

if 'history' not in globals():
    history = History()


class InputTextHistoryCommand(TextCommand):
    def run(self, edit, backwards=False):
        history.roll(backwards)
        self.view.erase(edit, Region(0, self.view.size()))
        self.view.insert(edit, 0, history.get())

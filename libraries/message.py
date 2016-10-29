# !/usr/bin/env python
# -*- coding: utf-8 -*-

import queue
from time import sleep
from threading import Thread
from .errors import error
from ..libraries import tools


class MessageQueue(object):
    """
    Print messages placed in the message queue
    """

    def __init__(self, callback=None):
        self.queue = queue.Queue()
        self.is_alive = False
        self.callback = callback

    def put(self, text, *args):
        """
        add a new text to the queue
        """
        if '\\n' in text:
            text = text.replace('\\n', '\n')

        if(text.strip()):
            self.queue.put(text)

    def start_print(self, once=False):
        """
        start a new thread to check and print the messages
        """
        if not self.is_alive:
            self.is_alive = True
            thread = Thread(target=lambda: self.put_print(once))
            thread.start()

    def put_print(self, once=False):
        """
        print the messages in the queue if once is True,
        it will prince only one time and the process will stop
        """
        if once:
            self.print_once()
        else:
            while self.is_alive:
                self.print_once()
                sleep(0.001)

    def print_once(self):
        """
        Print the message using the callback function if it's available
        """
        while not self.queue.empty():
            text = self.queue.get()
            if(self.callback):
                self.callback(text)
            else:
                print(text)

    def stop_print(self):
        """
        stop the queue while
        """
        while(not self.queue.empty()):
            sleep(0.05)
        self.is_alive = False


def print_error(code_error):
    print("=== MESSAGE ===")
    print(error[code_error])

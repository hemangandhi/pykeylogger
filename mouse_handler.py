#! /usr/bin/env python3

import time
from itertools import takewhile
from collections import deque
from keylogger import log
import ctypes as ct
from ctypes.util import find_library

class Display(ct.Structure): pass

class XButtonEvent(ct.Structure):
    _fields_ = [
            ('type', ct.c_int),
            ('serial', ct.c_ulong),
            ('send_event', ct.c_int),
            ('display', ct.POINTER(Display)),
            ('window', ct.c_ulong),
            ('root', ct.c_ulong),
            ('subwindow', ct.c_ulong),
            ('time', ct.c_ulong),
            ('x', ct.c_int),
            ('y', ct.c_int),
            ('x_root', ct.c_int),
            ('y_root', ct.c_int),
            ('state', ct.c_uint),
            ('button', ct.c_uint),
            ('same_screen', ct.c_int),
        ]

class XEvent(ct.Union):
    _fields_ = [
            ('type', ct.c_int),
            ('xbutton', XButtonEvent),
            ('pad', ct.c_long*24),
        ]

x11 = ct.cdll.LoadLibrary(find_library("X11"))
display = x11.XOpenDisplay(None)

class CommandReader:
    def __init__(self, handler):
        self.handler = handler
        self.cache = deque()
        self.done = False

    def __call__(self, time, mods, key):
        if key in self.handler:
            self.done = self.handler(self.cache, key)
            self.cache.clear()
        else:
            self.cache.append((key, mods))

    def __bool__(self):
        return self.done

class DefaultHandler:
    @staticmethod
    def get_window(xevent):
        xevent.xbutton.subwindow = x11.XDefaultRootWindow(display)
        xevent.xbutton.window = xevent.xbutton.subwindow

    @staticmethod
    def do_move(amt, dir):
        mov_vec = tuple(map(lambda x: x * amt, dir))
        x11.XWarpPointer(display, None, None, 0, 0, 0, 0, mov_vec[0], mov_vec[1])

    @staticmethod
    def do_press(click_char):
        evt = XEvent(type = 3)
        evt.xbutton.button = 1 if click_char else 2
        evt.xbutton.same_screen = True
        DefaultHandler.get_window(evt)
        evt.type = 4
        return x11.XSendEvent(display, 0, True, 4, ct.byref(evt))

    @staticmethod
    def do_release(click_char): #True for left click
        evt = XEvent(type = 3)
        evt.xbutton.button = 1 if click_char else 2
        evt.xbutton.same_screen = True
        DefaultHandler.get_window(evt)
        evt.type = 5
        return x11.XSendEvent(display, 0, True, 4, ct.byref(evt))

    @staticmethod
    def do_click(amt, char):
        for i in range(amt):
            DefaultHandler.do_press(char)
            DefaultHandler.do_release(char)

    def __contains__(self, key):
        return key in list('hjkliv') + ['<esc>']

    def __call__(self, cache, key):
        amt = (''.join(takewhile(str.isdigit, map(lambda x: x[0], cache))))
        if len(amt) > 0:
            amt = int(amt)
        else:
            amt = 1
        if key in 'hjkl':
            DefaultHandler.do_move(amt, {
                "h": (-1, 0),
                "j": (0, 1),
                "k": (0, -1),
                "l": (1, 0)}[key])
        elif key in 'iv':
            DefaultHandler.do_click(amt, key == 'i')
        return key == '<esc>'

if __name__ == "__main__":
    cmd = CommandReader(DefaultHandler())
    log(lambda : cmd, cmd, x11, display)

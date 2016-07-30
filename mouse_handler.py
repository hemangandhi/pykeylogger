#! /usr/bin/env python3

import time
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

dir_keymap = {
        "h": (-1, 0),
        "j": (0, 1),
        "k": (0, -1),
        "l": (1, 0)}

left_click = "i"
right_click = "v"
done = "<esc>"

def get_window(xevent):
    xevent.xbutton.subwindow = x11.XDefaultRootWindow(display)
    xevent.xbutton.window = xevent.xbutton.subwindow

def do_move(amt, dir):
    mov_vec = tuple(map(lambda x: x * amt, dir_keymap[dir]))
    x11.XWarpPointer(display, None, None, 0, 0, 0, 0, mov_vec[0], mov_vec[1])

def do_press(click_char):
    evt = XEvent(type = 3)
    evt.xbutton.button = 1 if click_char == left_click else 2
    evt.xbutton.same_screen = True
    get_window(evt)
    evt.type = 4
    return x11.XSendEvent(display, 0, True, 4, ct.byref(evt))

def do_release(click_char):
    evt = XEvent(type = 3)
    evt.xbutton.button = 1 if click_char == left_click else 2
    evt.xbutton.same_screen = True
    get_window(evt)
    evt.type = 5
    return x11.XSendEvent(display, 0, True, 4, ct.byref(evt))

def do_click(amt, char):
    for i in range(amt):
        do_press(char)
        do_release(char)

class CommandStateWrapper:
    def __init__(self):
        self.cache = deque()
        self.done = False

    def do_one_cmd(self, cmd, num):
        if len(num) <= 0: 
            val = 1
        else:
            val = int(num)
        if cmd in dir_keymap:
            do_move(val, cmd)
        elif cmd in [left_click, right_click]:
            do_click(val, cmd)

    def read_destroy_cache(self):
        num_acc = ""
        while len(self.cache) > 0:
            val = self.cache.popleft()
            if not val.isdigit():
                self.do_one_cmd(val, num_acc)
                num_acc = ""
            else:
                num_acc += val

    def next_char(self, char):
        if char is None:
            return
        if char != done:
            self.cache.append(char)
            if not char.isdigit():
                self.read_destroy_cache()
        else:
            self.done = True

    def __bool__(self):
        return self.done

if __name__ == "__main__":
    csw = CommandStateWrapper()
    log(csw.__bool__, lambda t, m, k: csw.next_char(k), x11, display)

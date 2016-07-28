#! /usr/bin/env python3

import uinput
from collections import deque
from keylogger import log

mouse_events = (
        uinput.REL_X, 
        uinput.REL_Y, 
        uinput.BTN_LEFT, 
        uinput.BTN_RIGHT)

dir_keymap = {
        "h": (-1, 0),
        "j": (0, 1),
        "k": (0, -1),
        "l": (1, 0)}

left_click = "i"
right_click = "v"
done = "<esc>"

def do_move(amt, dir):
    mov_vec = tuple(map(lambda x: x * amt, dir_keymap[dir]))
    with uinput.Device(mouse_events) as udev:
        udev.emit(uinput.REL_X, mov_vec[0], syn=False)
        udev.emit(uinput.REL_Y, mov_vec[1], syn=False)

def do_click(amt, click_char):
    with uinput.Device(mouse_events) as udev:
        for i in range(amt):
            if click_char == left_click:
                udev.emit_click(uinput.BTN_LEFT)
            elif click_char == right_click:
                udev.emit_click(uinput.BTN_RIGHT)

class CommandStateWrapper:
    def __init__(self):
        self.cache = deque()
        self.c_done = False
        self.abs_done = False

    def do_one_cmd(self, cmd, num):
        if len(num) <= 0: 
            val = 1
        else:
            val = int(num)
        if cmd in dir_keymap:
            do_move(val, cmd)
        else:
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
        if char != done:
            

from sdl2 import *
import ctypes

mode_key_handler = {}

def add_handler(mode,key, handlerfunc):
    if not mode in mode_key_handler:
        mode_key_handler[mode] = {}
    if key in mode_key_handler[mode]:#might be overkill
        raise KeyError("Key %s already in mode %s" % (key,mode))
    mode_key_handler[mode][key] = handlerfunc

active_modes = []

def activate_mode(mode):
    active_modes.append(mode)
def deactivate_mode(mode):
    active_modes.remove(mode)
def clear_mode(mode):
    mode_key_handler[mode].clear()

event = SDL_Event()
quit_handler = None

def handle_event():
    key_binds = {}
    for mode in active_modes:
        key_binds.update(mode_key_handler[mode])
    while True:
        if SDL_WaitEvent(ctypes.byref(event)) == 0:
           raise SDL_Exception()
        if event.type == SDL_QUIT:
            quit_handler()
            break
        elif event.type == SDL_KEYDOWN:
            keysym = event.key.keysym.sym
            if keysym in key_binds:
                key_binds[keysym]()
                break

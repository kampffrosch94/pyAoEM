import ctypes
import errors
import sdl2.events
import sdl2.keycode as keycode

controlled_entity = None

class BattleMode():
    pass
class StartMode():
    pass

mode_key_handler = {}

def add_handler(mode,handlerfunc,key,mod = keycode.KMOD_NONE):
    if not mode in mode_key_handler:
        mode_key_handler[mode] = {}
    if (key,mod) in mode_key_handler[mode]:#might be overkill
        raise KeyError("Key %s already in mode %s" % (key,mode))
    if not mod == keycode.KMOD_SHIFT:
        mode_key_handler[mode][(key,mod)] = handlerfunc
    else:
        #TODO read out modifierkeys correctly
        mode_key_handler[mode][(key,keycode.KMOD_LSHIFT)] = handlerfunc
        mode_key_handler[mode][(key,keycode.KMOD_RSHIFT)] = handlerfunc

active_modes = []

def activate_mode(mode):
    active_modes.clear() #TODO rework this hack
    active_modes.append(mode)
def deactivate_mode(mode):
    active_modes.remove(mode)
def clear_mode(mode):
    mode_key_handler[mode].clear()

event = sdl2.events.SDL_Event()

def _missing_quit():
    raise NotImplementedError("Override quit_handler")
quit_handler = _missing_quit

def handle_event():
    key_binds = {}
    for mode in active_modes:
        key_binds.update(mode_key_handler[mode])
    while True:
        if sdl2.events.SDL_WaitEvent(ctypes.byref(event)) == 0:
           raise errors.SDL_Exception()
        if event.type == sdl2.events.SDL_QUIT:
            quit_handler()
            break
        elif event.type == sdl2.events.SDL_KEYDOWN:
            key = event.key.keysym.sym
            mod = event.key.keysym.mod
            if (key,mod) in key_binds:
                key_binds[(key,mod)]()
                break

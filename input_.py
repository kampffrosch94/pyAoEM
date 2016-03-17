import ctypes
import sdl2
import errors
import movement
import utility

# general input

active_modes = []
mode_key_handler = {}

def _missing_quit():
    raise NotImplementedError("Override the quit_handler")

quit_handler = _missing_quit

class BattleMode():
    pass
class StartMode():
    pass

def activate_mode(mode):
    active_modes.clear() #TODO rework this hack
    active_modes.append(mode)
def deactivate_mode(mode):
    active_modes.remove(mode)
def clear_mode(mode):
    mode_key_handler[mode].clear()

def add_handler(mode,handlerfunc,key,mod = sdl2.KMOD_NONE):
    if not mode in mode_key_handler:
        mode_key_handler[mode] = {}
    if (key,mod) in mode_key_handler[mode]:#might be overkill
        raise KeyError("Key %s already in mode %s" % (key,mode))
    if not mod == sdl2.KMOD_SHIFT:
        mode_key_handler[mode][(key,mod)] = handlerfunc
    else:
        #TODO read out modifierkeys correctly
        mode_key_handler[mode][(key,sdl2.KMOD_LSHIFT)] = handlerfunc
        mode_key_handler[mode][(key,sdl2.KMOD_RSHIFT)] = handlerfunc

def handle_event():
    event = sdl2.SDL_Event()
    key_binds = {}
    for mode in active_modes:
        key_binds.update(mode_key_handler[mode])
    while True:
        if sdl2.SDL_WaitEvent(ctypes.byref(event)) == 0:
            raise errors.SDL_Exception()
        if event.type == sdl2.SDL_QUIT:
            quit_handler()
            break
        elif event.type == sdl2.SDL_KEYDOWN:
            key = event.key.keysym.sym
            mod = event.key.keysym.mod
            if (key,mod) in key_binds:
                key_binds[(key,mod)]()
                break

# Input for a controlled entity on the map

controlled_entity = None

def move_right():
    d = utility.Direction(1,0)
    movement.attack_or_move(controlled_entity,d)
def move_left():
    d = utility.Direction(-1,0)
    movement.attack_or_move(controlled_entity,d)
def move_up():
    d = utility.Direction(0,-1)
    movement.attack_or_move(controlled_entity,d)
def move_down():
    d = utility.Direction(0,1)
    movement.attack_or_move(controlled_entity,d)
def wait():
    d = utility.Direction(0,0)
    movement.attack_or_move(controlled_entity,d)

add_handler(BattleMode,move_right,sdl2.SDLK_l)
add_handler(BattleMode,move_left, sdl2.SDLK_h)
add_handler(BattleMode,move_up  , sdl2.SDLK_k)
add_handler(BattleMode,move_down, sdl2.SDLK_j)
add_handler(BattleMode,wait,      sdl2.SDLK_PERIOD)

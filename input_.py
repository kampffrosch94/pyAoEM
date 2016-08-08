import ctypes
import sdl2
from typing import Callable

# general input

key_handlers = {}  # type: Dict[str, Callable]


def _missing_quit():
    raise NotImplementedError("Override the quit_handler")


quit_handler = _missing_quit


def clear_handlers():
    key_handlers.clear()


def add_handler(handlerfunc, key, mod=sdl2.KMOD_NONE):
    if (key, mod) in key_handlers:
        raise KeyError("Key %s already in mode %s" % (key, mod))
    if not mod == sdl2.KMOD_SHIFT:
        key_handlers[(key, mod)] = handlerfunc
    else:
        # TODO read out modifierkeys correctly
        key_handlers[(key, sdl2.KMOD_LSHIFT)] = handlerfunc
        key_handlers[(key, sdl2.KMOD_RSHIFT)] = handlerfunc


def handle_event():
    """Busywait until SDL_Event in keyhandlers is received.
    Then the event_handler is invoked and it's returnvalue returned"""
    event = sdl2.SDL_Event()
    while True:
        if sdl2.SDL_WaitEvent(ctypes.byref(event)) == 0:
            raise Exception(sdl2.SDL_GetError())
        if event.type == sdl2.SDL_QUIT:
            quit_handler()
            return True
        elif event.type == sdl2.SDL_KEYDOWN:
            key = event.key.keysym.sym
            mod = event.key.keysym.mod
            if (key, mod) in key_handlers:
                return key_handlers[(key, mod)]()

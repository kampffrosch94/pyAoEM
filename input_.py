import ctypes
import sdl2
from typing import Callable


def _missing_quit():
    raise NotImplementedError("Override the quit_handler")


class InputHandler:
    def __init__(self):
        self.key_handlers = {}  # type: Dict[str, Callable]
        self.quit_handler = _missing_quit

    def clear_handlers(self):
        self.key_handlers.clear()

    def add_handler(self, handlerfunc, key, mod=sdl2.KMOD_NONE):
        if (key, mod) in self.key_handlers:
            raise KeyError("Key %s already in mode %s" % (key, mod))
        if not mod == sdl2.KMOD_SHIFT:
            self.key_handlers[(key, mod)] = handlerfunc
        else:
            # TODO read out modifierkeys correctly
            self.key_handlers[(key, sdl2.KMOD_LSHIFT)] = handlerfunc
            self.key_handlers[(key, sdl2.KMOD_RSHIFT)] = handlerfunc

    def handle_event(self):
        """Busywait until SDL_Event in keyhandlers is received.
        Then the event_handler is invoked and it's returnvalue returned"""
        event = sdl2.SDL_Event()
        while True:
            if sdl2.SDL_WaitEvent(ctypes.byref(event)) == 0:
                raise Exception(sdl2.SDL_GetError())
            if event.type == sdl2.SDL_QUIT:
                self.quit_handler()
                return True
            elif event.type == sdl2.SDL_KEYDOWN:
                key = event.key.keysym.sym
                mod = event.key.keysym.mod
                if mod in (sdl2.KMOD_NUM, sdl2.KMOD_NUM + sdl2.KMOD_LSHIFT,
                           sdl2.KMOD_NUM + sdl2.KMOD_RSHIFT):  # ignore numlock
                    mod -= sdl2.KMOD_NUM
                if (key, mod) in self.key_handlers:
                    return self.key_handlers[(key, mod)]()

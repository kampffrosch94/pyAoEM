from sdl2 import *

class SDL_Exception(Exception):
    def __init__(self):
        self.value = SDL_GetError()
    def __str__(self):
        return repr(self.value)

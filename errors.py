import sdl2

class SDL_Exception(Exception):
    def __init__(self):
        Exception.__init__()
        self.value = sdl2.SDL_GetError()
    def __str__(self):
        return repr(self.value)

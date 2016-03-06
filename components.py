from sdl2 import *
from utility import Position
from errors import SDL_Exception
from ctypes import byref
__doc__ = """This File holds the various components of the ecs.

A component should only hold data and no functionality if possible."""

class MapPos(Position):
    """The position of an entity on the map."""

class Buffer(object):
    """All Buffer components should inherit from this one."""
    pass

class BattleBuffer(Buffer):
    pass

class StartBuffer(Buffer):
    pass

class Graphic(object):
    """Contains a texture and the position where it should be rendered.
    
    Change x and y to change the position where the graphic will be
    rendered from the RenderSystem.
    """
    def __init__(self,texture,x=0,y=0,w=0,h=0,z=1):
        self.texture = texture
        if z < 0 or z > 1:
            raise NotImplementedError()
        self.z = z
        self.x = x
        self.y = y
        if w == 0 or h == 0:
            flags = Uint32()
            access = c_int()
            w = c_int()
            h = c_int()
            ret = SDL_QueryTexture(texture, byref(flags), 
                        byref(access), byref(w), byref(h))
            if ret == -1:
                raise SDL_Exception()
            w = w.value
            h = h.value

        self.w = w
        self.h = h
        self.src_rect = SDL_Rect(0,0,w,h)
        self._dest_rect = SDL_Rect(x,y,w,h)
        self.active = True #TODO make that a component

    @property
    def dest_rect(self):
        self._dest_rect.x = self.x
        self._dest_rect.y = self.y
        return self._dest_rect

    def destroy(self):
        SDL_DestroyTexture(self.texture)

class InputMap(object):
    """Contains mappings from inputkeys to functions."""
    def __init__(self):
        self.key_handlers = {}

    def add_key_handler(self,key_code, handlerfunc):
        self.key_handlers[key_code] = handlerfunc


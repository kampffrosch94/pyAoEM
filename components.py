from sdl2 import *
from utility import Position
__doc__ = """This File holds the various components of the ecs.

A component should only hold data and no functionality if possible."""

class MapPos(Position):
    """The position of an entity on the map."""


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
        self.src_rect = SDL_Rect(0,0,w,h)
        self._dest_rect = SDL_Rect(x,y,w,h)
        self.active = True

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


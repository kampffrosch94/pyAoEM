from sdl2 import *
import utility
__doc__ = """This File holds the various components of the ecs.

A component should only hold data and no functionality if possible."""

class MapPos(utility.Position):
    """The position of an entity on the map."""

class TileMap(object):
    """A map which holds tiles.
    
    self.textures is a list with textures
    self.tiles is a 2D grid which contains 
    texturenumbers for self.textures """
    def __init__(self,w,h,defaulttexture):
        self.w = w
        self.h = h
        self.tiles = [[0 for x in range(h)] for x in range(w)] 
        self.textures = [defaulttexture]

class Graphic(object):
    """Contains a texture and the position where it should be rendered.
    
    Change x and y to change the position where the graphic will be
    rendered from the RenderSystem.
    """
    def __init__(self,texture,x,y,width,height,z=0):
        self.texture = texture
        if z < 0 or z > 1:
            raise NotImplementedError()
        self.z = z
        self.x = x
        self.y = y
        self.src_rect = SDL_Rect(0,0,width,height)
        self._dest_rect = SDL_Rect(x,y,width,height)
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


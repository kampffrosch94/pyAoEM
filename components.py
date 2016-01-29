from sdl2 import *
from utility import Position

class MapComponent(object):
    """The position of an entity on the map."""
    def __init__(self,pos):
        self.pos = pos
        self.graphic_pos = Position(pos.x * 32, pos.y * 32)

    def graphic_pos_provider(self):
        #TODO do this as overloaded operation
        self.graphic_pos.x = self.pos.x * 32
        self.graphic_pos.y = self.pos.y * 32
        return self.graphic_pos;


class GraphicComponent(object):
    """Contains a texture and the position where it should be rendered."""
    def __init__(self,texture,x,y,width,height,z=0):
        self.texture = texture
        if z < 0 or z > 1:
            raise NotImplementedError()
        self.z = z
        self.src_rect = SDL_Rect(0,0,width,height)
        self._dest_rect = SDL_Rect(x,y,width,height)
        self.pos_provider = None

    def destroy(self):
        SDL_DestroyTexture(self.texture)

    @property
    def dest_rect(self):
        if self.pos_provider:
            pos = self.pos_provider() #returns utility.Position
            self._dest_rect.x = pos.x
            self._dest_rect.y = pos.y
        return self._dest_rect;

class InputComponent(object):
    """Contains mappings from inputkeys to functions."""
    def __init__(self):
        self.key_handlers = {}

    def add_key_handler(self,key_code, handlerfunc):
        self.key_handlers[key_code] = handlerfunc


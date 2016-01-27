from sdl2 import *

class GraphicComponent(object):
    def __init__(self,texture,width,height):
        self.texture = texture
        self.src_rect = SDL_Rect(0,0,width,height)
        self.dest_rect = SDL_Rect(0,0,width,height)


    def destroy(self):
        SDL_DestroyTexture(self.texture)

    @property
    def x(self):
        return self.dest_rect.x
    @x.setter
    def x(self,value):
        self.dest_rect.x = value

    @property
    def y(self):
        return self.dest_rect.y
    @y.setter
    def y(self,value):
        self.dest_rect.y = value

class InputComponent(object):
    def __init__(self):
        self.key_handlers = {}

    def add_key_handler(self,key_code, handlerfunc):
        self.key_handlers[key_code] = handlerfunc


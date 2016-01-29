from ecs import System
from sdl2 import *
from sdl2.sdlimage import *
import ctypes
from errors import SDL_Exception
from components import *

class InputSystem(System):
    """Takes SDL_Events and forwards them to listeners"""
    def __init__(self,world):
        System.__init__(self,"inputsystem",[InputComponent])
        self.world = world
        self.event = SDL_Event()

    def process(self,entities):
        if SDL_WaitEvent(ctypes.byref(self.event)) == 0:
           raise SDL_Exception()

        if self.event.type == SDL_QUIT:
            self.world.end()
        elif self.event.type == SDL_KEYDOWN:
            if self.event.key.keysym.sym == SDLK_q:
                self.world.end()
            else:
                for entity in entities:
                    binds = entity.inputcomponent.key_handlers
                    keysym = self.event.key.keysym.sym
                    if keysym in binds:
                        binds[keysym]()

class RenderSystem(System):
    """Renders textures to the window"""
    def __init__(self,world):
        System.__init__(self,"rendersystem",[GraphicComponent])

        IMG_Init(IMG_INIT_JPG)
        self.renderer = SDL_CreateRenderer(world.window,-1,
                SDL_RENDERER_ACCELERATED)

        if self.renderer == None:
            raise SDL_Exception()

    def process(self,entities):
        SDL_RenderClear(self.renderer)
        for entity in entities:#TODO splice this
            if entity.get(GraphicComponent).z == 0:
                SDL_RenderCopy(self.renderer,
                        entity.get(GraphicComponent).texture,
                        entity.get(GraphicComponent).src_rect,
                        entity.get(GraphicComponent).dest_rect)
        for entity in entities:#TODO splice this
            if entity.get(GraphicComponent).z == 1:
                SDL_RenderCopy(self.renderer,
                        entity.get(GraphicComponent).texture,
                        entity.get(GraphicComponent).src_rect,
                        entity.get(GraphicComponent).dest_rect)
        SDL_RenderPresent(self.renderer)

    def destroy(self):
        SDL_RenderClear(self.renderer)
        SDL_DestroyRenderer(self.renderer)
        IMG_Quit()

    def load_texture(self,path):
        path = str.encode(path)
        surface = IMG_Load(path)
        if surface == None:
            raise OSError("File "+path+" could not be loaded.")

        texture = SDL_CreateTextureFromSurface(self.renderer,surface) 
        if texture == None:
            raise SDL_Exception

        SDL_FreeSurface(surface)
        return texture
        

class WorldStepSystem(System):
    """The System which runs the gameloop"""
    def __init__(self,world,systemnames):
        System.__init__(self,"worldstepsystem")
        self.systemnames = systemnames
        self.world = world

    def process(self,entities):
        for sn in self.systemnames:
            self.world.invoke_system(sn)

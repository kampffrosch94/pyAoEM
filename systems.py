from ecs import System
from sdl2 import *
from sdl2.sdlimage import *
import ctypes
from errors import SDL_Exception
from components import *
from utility import Position,Rectangle

class InputSystem(System):
    """Takes SDL_Events and forwards them to listeners"""
    def __init__(self,world):
        System.__init__(self,[InputMap])
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
                    binds = entity.get(InputMap).key_handlers
                    keysym = self.event.key.keysym.sym
                    if keysym in binds:
                        binds[keysym]()

class MapSystem(System):
    """This system manages all entities which have a position on the map."""
    def __init__(self,world):
        System.__init__(self, [MapPos])
        self.map_entities = {}

    def process(self,entities):
        self.map_entities = {} #TODO dont always rebuild this
        for entity in entities:
            pos = entity.get(MapPos)
            if not pos in self.map_entities:
                self.map_entities[pos] = []
            self.map_entities[pos].append(entity)
    

class MapToGraphicSystem(System):
    """Converts coordinates on the map to coordinates in the window.
    
    Change root_pos to move the left upper corner of the visible map."""
    def __init__(self,world):
        System.__init__(self, [Graphic,MapPos])
        self.root_pos = Position(0,0)
        self.map_bounds = Rectangle(0,0,640,480)

    def process(self,entities):
        def in_view(gc:Graphic):
            bounds = self.map_bounds
            return (gc.x >= bounds.x and gc.x <= bounds.xe and
                    gc.y >= bounds.y and gc.y <= bounds.ye)

        for entity in entities:
            gc = entity.get(Graphic)
            mc = entity.get(MapPos)
            (gc.x,gc.y) = ((mc.x - self.root_pos.x)* 32,
                           (mc.y - self.root_pos.y)* 32)
            gc.active = in_view(gc)

class RenderSystem(System):
    """Renders textures to the window"""
    def __init__(self,world):
        System.__init__(self,[Graphic])

        IMG_Init(IMG_INIT_JPG)
        self.renderer = SDL_CreateRenderer(world.window,-1,
                SDL_RENDERER_ACCELERATED)

        if self.renderer == None:
            raise SDL_Exception()

    def render_graphics(self, graphics):
        for graphic in graphics:
            SDL_RenderCopy(self.renderer,
                    graphic.texture,
                    graphic.src_rect,
                    graphic.dest_rect)

    def process(self,entities):
        SDL_RenderClear(self.renderer)
        graphics = [e.get(Graphic) for e in entities 
                    if e.get(Graphic).active]
        z0 = filter((lambda g: g.z == 0),graphics)
        z1 = filter((lambda g: g.z == 1),graphics)
        self.render_graphics(z0)
        self.render_graphics(z1)
        SDL_RenderPresent(self.renderer)

    def destroy(self):
        SDL_RenderClear(self.renderer)
        SDL_DestroyRenderer(self.renderer)
        IMG_Quit()

    def load_graphic(self,path,x=0,y=0,z=0):
        path = str.encode(path)
        surface = IMG_Load(path)
        if surface == None:
            raise OSError("File "+path+" could not be loaded.")

        texture = SDL_CreateTextureFromSurface(self.renderer,surface) 
        if texture == None:
            raise SDL_Exception

        graphic = Graphic(texture,x,y,surface.contents.w,
                                      surface.contents.h,z)
        SDL_FreeSurface(surface)
        return graphic
        

class WorldStepSystem(System):
    """The System which runs the gameloop"""
    def __init__(self,world,systems):
        System.__init__(self)
        self.systems = systems
        self.world = world

    def process(self,entities):
        for s in self.systems:
            self.world.invoke_system(s.__class__.__name__.lower())

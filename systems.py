from ecs import System, Entity
from sdl2 import *
from sdl2.sdlimage import *
from sdl2.sdlttf import *
import ctypes
from errors import SDL_Exception
from components import *
from utility import Position,Rectangle
import sdl_manager

class InputSystem(System):
    """Takes SDL_Events and forwards them to listeners"""
    def __init__(self,world):
        System.__init__(self,[InputMap])
        self.world = world
        self.event = SDL_Event()

    def process(self,entities):
        key_binds = {}
        for entity in entities:
            key_binds.update(entity.get(InputMap).key_handlers)
        while True:
            if SDL_WaitEvent(ctypes.byref(self.event)) == 0:
               raise SDL_Exception()

            if self.event.type == SDL_QUIT:
                self.world.end()
                break
            elif self.event.type == SDL_KEYDOWN:
                keysym = self.event.key.keysym.sym
                if keysym in key_binds:
                    key_binds[keysym]()
                    break

class TileMap(object):
    #TODO move to componenets or merge with the system
    """A map which holds tiles.
    
    self.textures is a list with textures
    self.tiles is a 2D grid which contains 
    texturenumbers for self.textures """
    def __init__(self,w,h,defaulttexture):
        self.w = w
        self.h = h
        self.tiles = [[0 for x in range(h)] for x in range(w)] 
        self.textures = [defaulttexture]
        self.root_pos = Position(0,0)

class TileMapSystem(System):
    def __init__(self,world):
        System.__init__(self, [Graphic,TileMap])
        self.world = world

    def process(self,entities):
        if len(entities) != 1:
            raise NotImplementedError()
        tilemap_entity = entities[0]
        tilemap_gc     = tilemap_entity.get(Graphic)
        tilemap        = tilemap_entity.get(TileMap)

        renderer = sdl_manager.renderer
        SDL_SetRenderTarget(renderer,tilemap_gc.texture)
        SDL_RenderClear(renderer)

        src_rect = SDL_Rect(0,0,32,32)
        dest_rect = SDL_Rect(0,0,32,32)
        root_pos = tilemap.root_pos

        for x in range(root_pos.x,root_pos.x + 20):
            if x >= 0 and x < tilemap.w:
                row = tilemap.tiles[x]
                for y in range(root_pos.y,root_pos.y + 15):
                    if y >= 0 and y < tilemap.h:
                        texture = tilemap.textures[row[y]]
                        dest_rect.x = (x-root_pos.x) * 32
                        dest_rect.y = (y-root_pos.y) * 32
                        SDL_RenderCopy( renderer,
                                        texture,
                                        src_rect,
                                        dest_rect)
        SDL_SetRenderTarget(renderer,None)

class MapSystem(System): #TODO find better name
    """This system buffers all entities which have a position on the map."""
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
            return (gc.x >= bounds.x and gc.x < bounds.xe and
                    gc.y >= bounds.y and gc.y < bounds.ye)

        for entity in entities:
            gc = entity.get(Graphic)
            mc = entity.get(MapPos)
            (gc.x,gc.y) = ((mc.x - self.root_pos.x)* 32,
                           (mc.y - self.root_pos.y)* 32)
            gc.active = in_view(gc)

class LogSystem(System):
    """Holds and Renders the Messagelog."""
    def __init__(self,world):
        System.__init__(self)
        self.messages = []
        world.message_log = self

        self.texture = SDL_CreateTexture(
                sdl_manager.renderer,
                SDL_PIXELFORMAT_RGBA8888,
                SDL_TEXTUREACCESS_TARGET,160,480)
        e = Entity(world)
        g = Graphic(self.texture,x=0,y=480)
        e.set(g)

    def add_msg(self,msg):
        self.messages.append(msg)
        if len(self.messages) > 9:
            del self.messages[0]
        self.dirty = True

    def process(self,entities=None):
        if self.dirty:
            renderer = sdl_manager.renderer
            SDL_SetRenderTarget(renderer,self.texture)
            SDL_RenderClear(renderer)
            y = 0
            for msg in self.messages:
                g = sdl_manager.create_text_graphic(msg)
                g.y = y
                SDL_RenderCopy( renderer,
                                g.texture,
                                g.src_rect,
                                g.dest_rect)
                y += g.h
                g.destroy()
            SDL_SetRenderTarget(renderer,None)
            self.dirty = False

class RenderSystem(System):
    """Renders textures to the window"""
    def __init__(self,world):
        System.__init__(self,[Graphic])

        IMG_Init(IMG_INIT_JPG)
        self.world = world

    def render_graphics(self, graphics):
        renderer = sdl_manager.renderer
        for graphic in graphics:
            SDL_RenderCopy(renderer,
                    graphic.texture,
                    graphic.src_rect,
                    graphic.dest_rect)
        
    def process(self,entities):
        renderer = sdl_manager.renderer
        SDL_RenderClear(renderer)
        graphics = [e.get(Graphic) for e in entities 
                    if e.get(Graphic).active]
        z0 = filter((lambda g: g.z == 0),graphics)
        z1 = filter((lambda g: g.z == 1),graphics)
        self.render_graphics(z0)
        self.render_graphics(z1)
        SDL_RenderPresent(renderer)

    def load_graphic(self,texture_name,x=0,y=0,z=0):
        texture = sdl_manager.load_texture(texture_name)
        graphic = Graphic(texture,x,y,32,32,z)
        return graphic
        

class WorldStepSystem(System):
    """The System which runs the gameloop"""
    def __init__(self,world,systems):
        System.__init__(self)
        self.systems = [s.__class__ for s in systems]
        self.world = world

    def process(self,entities):
        for s in self.systems:
            self.world.invoke_system(s)

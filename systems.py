from ecs import System, Entity
from sdl2 import *
import ctypes
from errors import SDL_Exception
from components import *
from utility import Position,Rectangle
import sdl_manager
from sdl_manager import renderer
import map_manager
import input_manager
import battle_log

class InputSystem(System):
    """Takes SDL_Events and forwards them to listeners"""
    def __init__(self):
        System.__init__(self,[])

    def process(self,entities):
        input_manager.handle_event()


class MapToGraphicSystem(System):
    """Converts coordinates on the map to coordinates in the window.
    
    Change root_pos to move the left upper corner of the visible map."""
    def __init__(self,world):
        System.__init__(self, [Graphic,MapPos])
        self.map_bounds = Rectangle(0,0,640,480)

    def process(self,entities):
        def in_view(gc:Graphic):
            bounds = self.map_bounds
            return (gc.x >= bounds.x and gc.x < bounds.xe and
                    gc.y >= bounds.y and gc.y < bounds.ye)

        root_pos = map_manager.current_map.root_pos
        for entity in entities:
            gc = entity.get(Graphic)
            mc = entity.get(MapPos)
            (gc.x,gc.y) = ((mc.x - root_pos.x)* 32,
                           (mc.y - root_pos.y)* 32)
            gc.active = in_view(gc)


class RenderSystem(System):
    """Renders textures to the window"""
    def __init__(self,extra_cts = []):
        cts = [Graphic]
        cts.extend(extra_cts)
        System.__init__(self,cts)

    def render_graphics(self, graphics):
        renderer = sdl_manager.renderer
        for graphic in graphics:
            SDL_RenderCopy(renderer,
                    graphic.texture,
                    graphic.src_rect,
                    graphic.dest_rect)
        
    def render_entities(self,entities):
        graphics = [e.get(Graphic) for e in entities 
                    if e.get(Graphic).active]
        z0 = filter((lambda g: g.z == 0),graphics)
        z1 = filter((lambda g: g.z == 1),graphics)
        self.render_graphics(z0)
        self.render_graphics(z1)

    def process(self,entities):
        SDL_RenderClear(renderer)
        self.render_entities(entities)
        SDL_RenderPresent(renderer)

class BattleRenderSystem(RenderSystem):
    def __init__(self):
        RenderSystem.__init__(self,[BattleBuffer])

    def process(self,entities):
        SDL_RenderClear(renderer)
        map_manager.current_map.render()
        self.render_entities(entities)
        battle_log.render()
        SDL_RenderPresent(renderer)

class StartRenderSystem(RenderSystem):
    def __init__(self):
        RenderSystem.__init__(self,[StartBuffer])

class WorldStepSystem(System):
    """The System which runs the gameloop"""
    def __init__(self,world,systems):
        System.__init__(self)
        self.systems = [s.__class__ for s in systems]
        self.world = world

    def process(self,entities):
        for s in self.systems:
            self.world.invoke_system(s)

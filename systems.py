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
from game_systems import *

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
        self.header = sdl_manager.create_text_graphic(
                "Attack on Evil Mountain\n--Unfinished Business--\n\n")
        self.header.x,self.header.y = 200,150

        self.choice = sdl_manager.create_text_graphic(
                "a) Fight against the GIANT newts of Evil Mountain.\n"+
                "b) Flee in terror. (Quit.)")
        self.choice.x,self.choice.y = 100,300

        self.game_ended = False

    def process(self,entities):
        SDL_RenderClear(renderer)
        SDL_RenderCopy(renderer,
                self.header.texture,
                self.header.src_rect,
                self.header.dest_rect)
        if not self.game_ended:
            SDL_RenderCopy(renderer,
                    self.choice.texture,
                    self.choice.src_rect,
                    self.choice.dest_rect)
        else:
            SDL_RenderCopy(renderer,
                    self.end_game.texture,
                    self.end_game.src_rect,
                    self.end_game.dest_rect)
        SDL_RenderPresent(renderer)

    def set_end_game(self,text):
        if hasattr(self,"end_game"):
            SDL_DestroyTexture(self.end_game.texture)
        self.end_game = sdl_manager.create_text_graphic(text +
                "\n\nb) to quit")
        self.end_game.x,self.end_game.y = 100,300
        self.game_ended= True

class WorldStepSystem(System):
    """The System which runs the gameloop"""
    def __init__(self,world,systems):
        System.__init__(self)
        self.systems = [s.__class__ for s in systems]
        self.world = world

    def process(self,entities):
        for s in self.systems:
            self.world.invoke_system(s)

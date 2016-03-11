from sdl2 import *
from sdl_manager import renderer
from utility import Position
import sdl_manager
import dungeon_gen
dungeon_gen.seed()

current_map = None
map_src = SDL_Rect(w=640,h=480)
map_dest = SDL_Rect(x=0,y=0,w=map_src.w,h=map_src.h)
map_texture = SDL_CreateTexture(
        renderer,
        SDL_PIXELFORMAT_RGBA8888,
        SDL_TEXTUREACCESS_TARGET,map_src.w,map_src.h)

default_floor = sdl_manager.load_texture("cobble_blood1")
default_wall = sdl_manager.load_texture("lair0")

class TileMap(object):
    """A map which holds tiles.
    
    self.textures is a list with textures
    self.tiles is a 2D grid which contains 
    texturenumbers for self.textures """
    def __init__(self,w,h):
        self.w = w
        self.h = h
        g_map = dungeon_gen.checked_cellular_automaton(w,h)
        self.tiles = g_map #needs more variety
        self.textures = [default_floor,default_wall]
        self.root_pos = Position(0,0)

    def update(self):
        SDL_SetRenderTarget(renderer,map_texture)
        SDL_RenderClear(renderer)

        src_rect = SDL_Rect(0,0,32,32)
        dest_rect = SDL_Rect(0,0,32,32)
        root_pos = self.root_pos

        for x in range(root_pos.x,root_pos.x + 20):
            for y in range(root_pos.y,root_pos.y + 15):
                if (x,y) in self.tiles:
                    texture = self.textures[self.tiles[(x,y)]]
                    dest_rect.x = (x-root_pos.x) * 32
                    dest_rect.y = (y-root_pos.y) * 32
                    SDL_RenderCopy( renderer,
                                    texture,
                                    src_rect,
                                    dest_rect)
        SDL_SetRenderTarget(renderer,None)

    def render(self):
        self.update()
        SDL_RenderCopy(renderer,map_texture,map_src,map_dest)

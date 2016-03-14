import sdl_manager
import dungeon_gen
import sdl2
import utility
dungeon_gen.seed()

current_map = None
map_src = sdl2.SDL_Rect(w=640,h=480)
map_dest = sdl2.SDL_Rect(x=0,y=0,w=map_src.w,h=map_src.h)
map_texture = sdl2.SDL_CreateTexture(
        sdl_manager.renderer,
        sdl2.SDL_PIXELFORMAT_RGBA8888,
        sdl2.SDL_TEXTUREACCESS_TARGET,map_src.w,map_src.h)

default_floor = sdl_manager.load_texture("cobble_blood1")
default_wall = sdl_manager.load_texture("lair0")

class TileMap(object):
    """A map which holds tiles.
    
    self.textures is a list with textures
    self.tiles is a 2D grid which contains 
    texturenumbers for self.textures """
    def __init__(self,w,h,wall_chance):
        self.w = w
        self.h = h
        g_map = dungeon_gen.checked_cellular_automaton(w,h,wall_chance)
        self.wall_map = g_map
        self.tiles = g_map #needs more variety
        self.textures = [default_floor,default_wall]
        self.root_pos = utility.Position(0,0)

    def is_wall(self,pos):
        return self.wall_map[pos]

    def djikstra_map(self,start_positions : iter):
        return dungeon_gen.djikstra_map(self.wall_map,start_positions)

    def neighbors(self,pos):
        return dungeon_gen.neighbors(self.wall_map,pos)

    def update(self):
        sdl2.SDL_SetRenderTarget(sdl_manager.renderer,map_texture)
        sdl2.SDL_RenderClear(sdl_manager.renderer)

        src_rect = sdl2.SDL_Rect(0,0,32,32)
        dest_rect = sdl2.SDL_Rect(0,0,32,32)
        root_pos = self.root_pos

        for x in range(root_pos.x,root_pos.x + 20):
            for y in range(root_pos.y,root_pos.y + 15):
                if (x,y) in self.tiles:
                    texture = self.textures[self.tiles[(x,y)]]
                    dest_rect.x = (x-root_pos.x) * 32
                    dest_rect.y = (y-root_pos.y) * 32
                    sdl2.SDL_RenderCopy(sdl_manager.renderer,
                                        texture,
                                        src_rect,
                                        dest_rect)
        sdl2.SDL_SetRenderTarget(sdl_manager.renderer,None)

    def render(self):
        self.update()
        sdl2.SDL_RenderCopy(sdl_manager.renderer,map_texture,
                map_src,map_dest)

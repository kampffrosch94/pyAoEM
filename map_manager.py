import sdl2
import res
import dungeon_gen
import utility
MAP_WIDTH  = 20
MAP_HEIGHT = 15
TILE_HEIGHT= 32
TILE_WIDTH = 32
dungeon_gen.seed()

current_map = None
map_graphic = res.create_graphic(0,0,640,480)
default_floor = res.load_graphic("cobble_blood1")
default_wall = res.load_graphic("lair0")

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
        self.tile_graphics = [default_floor,default_wall]
        self.root_pos = utility.Position(0,0)

    def is_wall(self,pos):
        return self.wall_map[pos]

    def djikstra_map(self,start_positions : iter):
        return dungeon_gen.djikstra_map(self.wall_map,start_positions)

    def neighbors(self,pos):
        return dungeon_gen.neighbors(self.wall_map,pos)

    def update(self):
        map_graphic.make_render_target()
        sdl2.SDL_RenderClear(res.renderer)

        root_pos = self.root_pos
        for x in range(root_pos.x,root_pos.x + MAP_WIDTH):
            for y in range(root_pos.y,root_pos.y + MAP_HEIGHT):
                if (x,y) in self.tiles:
                    g = self.tile_graphics[self.tiles[(x,y)]]
                    g.x = (x-root_pos.x) * TILE_WIDTH
                    g.y = (y-root_pos.y) * TILE_HEIGHT
                    g.render()
        sdl2.SDL_SetRenderTarget(res.renderer,None)

    def render(self):
        self.update()
        map_graphic.render()

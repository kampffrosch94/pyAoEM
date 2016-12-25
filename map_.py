from typing import Iterable

import dungeon_gen
import res
import util

# map display constants
MAP_WIDTH = 20
MAP_HEIGHT = 15
TILE_HEIGHT = 32
TILE_WIDTH = 32
dungeon_gen.seed()

map_graphic = res.create_graphic(0, 0, 640, 480)
default_floor = res.load_graphic("cobble_blood1")
default_wall = res.load_graphic("lair0")


class TileMap(object):
    """A map which holds tiles.

    self.textures is a list with textures
    self.tiles is a 2D grid which contains
    texturenumbers for self.textures """

    def __init__(self, w, h, wall_chance=42):
        self.w = w
        self.h = h
        self.wall_chance = wall_chance
        g_map = dungeon_gen.checked_cellular_automaton(self.w, self.h,
                                                       self.wall_chance)
        self.wall_map = g_map
        self.tiles = g_map  # needs more variety
        self.tile_graphics = [default_floor, default_wall]
        self.root_pos = util.Position(0, 0)

    def regen(self):
        g_map = dungeon_gen.checked_cellular_automaton(self.w, self.h,
                                                       self.wall_chance)
        self.wall_map = g_map
        self.tiles = g_map  # needs more variety
        self.root_pos = util.Position(0, 0)

    def is_wall(self, pos):
        return self.wall_map[pos]

    def is_visible(self, pos):
        return (self.root_pos.x <= pos.x < self.root_pos.x + MAP_WIDTH and
                self.root_pos.y <= pos.y < self.root_pos.y + MAP_HEIGHT)

    def djikstra_map(self, start_positions: Iterable):
        return dungeon_gen.djikstra_map(self.wall_map, start_positions)

    def neighbors(self, pos):
        return dungeon_gen.neighbors(self.wall_map, pos)

    def update(self):
        map_graphic.make_render_target()
        res.render_clear()

        root_pos = self.root_pos
        for x in range(root_pos.x, root_pos.x + MAP_WIDTH):
            for y in range(root_pos.y, root_pos.y + MAP_HEIGHT):
                if (x, y) in self.tiles:
                    g = self.tile_graphics[self.tiles[(x, y)]]
                    g.x = (x - root_pos.x) * TILE_WIDTH
                    g.y = (y - root_pos.y) * TILE_HEIGHT
                    g.render()

        res.reset_render_target()

    @staticmethod
    def render():
        map_graphic.render()

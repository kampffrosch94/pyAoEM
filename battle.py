import ecs
import res
import map_
import game
import utility
import battle_log

map_bounds = utility.Rectangle(0,0,map_.MAP_WIDTH,map_.MAP_HEIGHT)

def in_view(pos):
    return map_bounds.in_bounds(pos)

class BattleRenderSystem(ecs.System):
    def __init__(self):
        super().__init__([res.Graphic, game.MapPos, BattleBuffer])

    def render_entities(self,entities):
        graphics = [e.get(res.Graphic) for e in entities
                    if in_view(e.get(game.MapPos))]
        graphics = []
        for e in entities:
            mp = e.get(game.MapPos)
            if in_view(mp):
                g = e.get(res.Graphic)
                g.x = map_.TILE_WIDTH * mp.x
                g.y = map_.TILE_HEIGHT * mp.y
                graphics.append(g)

        z0 = [g for g in graphics if g.z == 0]
        z1 = [g for g in graphics if g.z == 1]
        for g in z0:
            g.render()
        for g in z1:
            g.render()

    def process(self,entities):
        res.render_clear()
        map_.current_map.render()
        self.render_entities(entities)
        battle_log.render()
        res.render_present()

# Components

class BattleBuffer(object):
    pass

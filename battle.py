import sdl2
import ecs
import res
import components
import map_manager
import utility
import battle_log

map_bounds = utility.Rectangle(0,0,20,15)

def in_view(pos):
    bounds = map_bounds
    return (pos.x >= bounds.x and pos.x < bounds.xe and
            pos.y >= bounds.y and pos.y < bounds.ye)

class BattleRenderSystem(ecs.System):
    def __init__(self):
        super().__init__([res.Graphic,components.MapPos,
                          components.BattleBuffer])

    def render_entities(self,entities):
        graphics = [e.get(res.Graphic) for e in entities
                    if in_view(e.get(components.MapPos))]
        graphics = []
        for e in entities:
            mp = e.get(components.MapPos)
            if in_view(mp):
                g = e.get(res.Graphic)
                g.x = map_manager.TILE_WIDTH * mp.x
                g.y = map_manager.TILE_HEIGHT * mp.y
                graphics.append(g)

        z0 = [g for g in graphics if g.z == 0]
        z1 = [g for g in graphics if g.z == 1]
        for g in z0:
            g.render()
        for g in z1:
            g.render()

    def process(self,entities):
        sdl2.SDL_RenderClear(res.renderer)
        map_manager.current_map.render()
        self.render_entities(entities)
        battle_log.render()
        sdl2.SDL_RenderPresent(res.renderer)

import sdl2
import ecs
import components
import utility
import res
import map_manager
import battle_log

class MapToGraphicSystem(ecs.System):
    """Converts coordinates on the map to coordinates in the window.

    Change root_pos to move the left upper corner of the visible map."""
    def __init__(self):
        ecs.System.__init__(self, [components.Graphic,components.MapPos])
        self.map_bounds = utility.Rectangle(0,0,640,480)

    def process(self,entities):
        def in_view(gc:components.Graphic):
            bounds = self.map_bounds
            return (gc.x >= bounds.x and gc.x < bounds.xe and
                    gc.y >= bounds.y and gc.y < bounds.ye)

        root_pos = map_manager.current_map.root_pos
        for entity in entities:
            gc = entity.get(components.Graphic)
            mc = entity.get(components.MapPos)
            (gc.x,gc.y) = ((mc.x - root_pos.x)* 32,
                           (mc.y - root_pos.y)* 32)
            gc.active = in_view(gc)


class RenderSystem(ecs.System):
    """Renders textures to the window"""
    def __init__(self,extra_cts = None):
        cts = [components.Graphic]
        if not extra_cts is None:
            cts.extend(extra_cts)
        ecs.System.__init__(self,cts)

    def render_graphics(self, graphics):
        for graphic in graphics:
            sdl2.SDL_RenderCopy(
                res.renderer,
                graphic.texture,
                graphic.src_rect,
                graphic.dest_rect)

    def render_entities(self,entities):
        graphics = [e.get(components.Graphic) for e in entities
                    if e.get(components.Graphic).active]
        z0 = filter((lambda g: g.z == 0),graphics)
        z1 = filter((lambda g: g.z == 1),graphics)
        self.render_graphics(z0)
        self.render_graphics(z1)

    def process(self,entities):
        sdl2.SDL_RenderClear(res.renderer)
        self.render_entities(entities)
        sdl2.SDL_RenderPresent(res.renderer)

class BattleRenderSystem(RenderSystem):
    def __init__(self):
        RenderSystem.__init__(self,[components.BattleBuffer])

    def process(self,entities):
        sdl2.SDL_RenderClear(res.renderer)
        map_manager.current_map.render()
        self.render_entities(entities)
        battle_log.render()
        sdl2.SDL_RenderPresent(res.renderer)

class StartRenderSystem(RenderSystem):
    def __init__(self):
        RenderSystem.__init__(self,[components.StartBuffer])
        self.header = res.create_text_graphic(
            "Attack on Evil Mountain\n--Unfinished Business--\n\n")
        self.header.x,self.header.y = 200,150

        self.choice = res.create_text_graphic(
            "a) Fight against the GIANT newts of Evil Mountain.\n"+
            "b) Flee in terror. (Quit.)")
        self.choice.x,self.choice.y = 100,300

        self.game_ended = False

    def process(self,entities):
        sdl2.SDL_RenderClear(res.renderer)
        sdl2.SDL_RenderCopy(
            res.renderer,
            self.header.texture,
            self.header.src_rect,
            self.header.dest_rect)
        if not self.game_ended:
            sdl2.SDL_RenderCopy(
                res.renderer,
                self.choice.texture,
                self.choice.src_rect,
                self.choice.dest_rect)
        else:
            sdl2.SDL_RenderCopy(
                res.renderer,
                self.end_game.texture,
                self.end_game.src_rect,
                self.end_game.dest_rect)
        sdl2.SDL_RenderPresent(res.renderer)

    def set_end_game(self,text):
        if hasattr(self,"end_game"):
            sdl2.SDL_DestroyTexture(self.end_game.texture)
        self.end_game = res.create_text_graphic(
            text +
            "\n\nb) to quit")
        self.end_game.x,self.end_game.y = 100,300
        self.game_ended= True

class WorldStepSystem(ecs.System):
    """The System which runs the gameloop"""
    def __init__(self,world,systems):
        ecs.System.__init__(self)
        self.systems = [s.__class__ for s in systems]
        self.world = world

    def process(self,entities):
        for s in self.systems:
            self.world.invoke_system(s)

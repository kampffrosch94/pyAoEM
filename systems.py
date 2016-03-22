import sdl2
import ecs
import components
import utility
import res
import map_manager
import battle_log

class StartRenderSystem(ecs.System):
    def __init__(self):
        super().__init__([components.StartBuffer])
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

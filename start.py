import sdl2
import ecs
import res
import input_
import battle

# Components

class StartBuffer(object):
    pass

# System

class StartRenderSystem(ecs.System):
    def __init__(self):
        super().__init__([StartBuffer])
        self.header = res.create_text_graphic(
            "Attack on Evil Mountain\n--Unfinished Business--\n\n",
            x=200, y=150)

        self.choice = res.create_text_graphic(
            "a) Fight against the GIANT newts of Evil Mountain.\n"+
            "b) Flee in terror. (Quit.)",
            x=100, y=300)

    def process(self,entities):
        res.render_clear()
        self.header.render()
        self.choice.render()
        res.render_present()
        input_.handle_event()

    def set_end_game(self,victory):
        if victory:
            text = "You win a glorious VICTORY!!!"
        else:
            text = "You were DEFEATED!!!"
        self.choice.destroy() #TODO remove on removal of destroy
        self.choice = res.create_text_graphic(
            text +
            "\n\nb) to quit",
            x=100, y=300)

system = StartRenderSystem()

# Keybinds

class StartMode():
    pass

def start_game():
    system.active  = False
    battle.activate()

def quit():
    input_.quit_handler()

input_.add_handler(StartMode,start_game,sdl2.SDLK_a)
input_.add_handler(StartMode,quit,sdl2.SDLK_b)
input_.activate_mode(StartMode)

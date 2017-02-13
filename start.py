"""The startmenu"""
import sdl2
import res
from input_ import InputHandler
import ecs

title = res.create_text_graphic(
    "Attack on Evil Mountain\n--Unfinished Business--\n\n",
    x=200, y=150)

choice = res.create_text_graphic(
    "a) Fight against the GIANT newts of Evil Mountain.\n" +
    "b) Flee in terror. (Quit.)",
    x=100, y=300)

input_handler = InputHandler()




def to_battle():
    print("Switch to battlescene.")
    import battle
    battle.activate(world)


def render():
    res.render_clear()
    title.render()
    choice.render()
    res.render_present()


def main_loop():
    render()
    input_handler.handle_event()


world = None


def activate(w: ecs.World):
    global world
    world = w

    def quit_():
        w.end()

    input_handler.quit_handler = quit
    input_handler.add_handler(to_battle, sdl2.SDLK_a)
    input_handler.add_handler(quit_, sdl2.SDLK_b)
    render()
    world.main_loop = main_loop

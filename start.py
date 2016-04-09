"""The startmenu"""
import sdl2
import res
import input_

title = res.create_text_graphic(
    "Attack on Evil Mountain\n--Unfinished Business--\n\n",
    x=200, y=150)

choice = res.create_text_graphic(
    "a) Fight against the GIANT newts of Evil Mountain.\n"+
    "b) Flee in terror. (Quit.)",
    x=100, y=300)

def quit_():
    input_.quit_handler()

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
    print("TODO enter main loop")
    render()
    input_.handle_event()

world = None

def activate(w=None):
    if w is not None:
        global world 
        world = w

    input_.clear_handlers()
    input_.add_handler(to_battle, sdl2.SDLK_a)
    input_.add_handler(quit_, sdl2.SDLK_b)
    render()
    world.main_loop = main_loop

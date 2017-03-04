import sdl2
import res
from input_ import InputHandler
import ecs

title = None
_world = None  # type: ecs.World
input_handler = InputHandler()

choice = res.create_text_graphic(
    "a) Alright. (Quit.)",
    x=100, y=200)


def quit_():
    _world.end()


def render():
    res.render_clear()
    title.render()
    choice.render()
    res.render_present()


def activate(world: ecs.World):
    global title, _world
    _world = world
    text = "You die a horrible death!"
    title = res.create_text_graphic(
        text,
        x=100, y=150)
    input_handler.add_handler(quit_, sdl2.SDLK_a)
    render()
    input_handler.handle_event()()

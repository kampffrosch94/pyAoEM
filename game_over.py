import sdl2
import res
import input_

title = None
choice = res.create_text_graphic(
    "a) Alright. (Quit.)",
    x=100, y=200)

def quit_():
    input_.quit_handler()

def render():
    res.render_clear()
    title.render()
    choice.render()
    res.render_present()

def activate(won):
    global title
    if won:
        text = "You win a glorious victory!"
    else:
        text = "You lose."
    title = res.create_text_graphic(
        text,
        x=100, y=150)
    input_.clear_handlers()
    input_.add_handler(quit_, sdl2.SDLK_a)
    render()
    input_.handle_event()

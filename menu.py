import sdl2
import res
import input_

_CHOICE_KEYS = [sdl2.SDLK_a,
               sdl2.SDLK_b,
               sdl2.SDLK_c,
               sdl2.SDLK_d,
               sdl2.SDLK_e,
               sdl2.SDLK_f,
               sdl2.SDLK_g,
               ]
_CHOICE_CHARS = ["a", "b", "c", "d", "e", "f", "g"]


class ChoiceMenu:
    def __init__(self, x, y, w, h, header, choices, cancel = False):
        if len(choices) > len(_CHOICE_KEYS):
            raise NotImplementedError("Not enough keys for this many choices")
        
        self.graphic = res.create_graphic(x, y, w, h)
        self.header  = res.create_text_graphic(header, 20, 20,
                                               max_width = w - 20)
        choice_text = ""
        i = 0
        for c in choices:
            choice_text += _CHOICE_CHARS[i] + ") " + c + "\n"
            i = i + 1
        self.choices = res.create_text_graphic(choice_text, 20, 50,
                                               max_width = w - 20)
        self.choice_count = i
        self.cancel = cancel

    def bind_keys(self):
        input_.clear_handlers()
        for i in range(self.choice_count):
            f = (lambda i=i: i)
            input_.add_handler(f, _CHOICE_KEYS[i])
        if self.cancel is True:
            input_.add_handler(lambda: None, sdl2.SDLK_ESCAPE)

    def choose(self):
        self.update()
        self.render()
        self.bind_keys()
        return input_.handle_event()

    def update(self):
        self.graphic.make_render_target()
        res.render_clear()
        self.header.render()
        self.choices.render()
        res.reset_render_target()

    def render(self):
        self.graphic.render()
        res.render_present()

# Test code
def _test():
    head = "Example Header."
    choices = ["Take this.", "Body Slam",
               "I don't know anymore."]
    m = ChoiceMenu(0,0,500,500,head,choices)
    m.render()
    print("You chose Nr: %s" % m.choose())

if __name__ == "__main__":
    _test()

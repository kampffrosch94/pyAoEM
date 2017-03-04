import sdl2
import res
from input_ import InputHandler

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
    def __init__(self, x, y, w, h, header, choices, cancel=False,
                 cancel_result=None):
        """The choices are a list of Pairs(choice_text, value)"""
        if len(choices) > len(_CHOICE_KEYS):
            raise NotImplementedError("Not enough keys for this many choices")
        if len(choices) < 1:
            raise AssertionError("I have no choice.")

        self.graphic = res.create_graphic(x, y, w, h)
        self.header = res.create_text_graphic(header, 20, 20,
                                              max_width=w - 20)
        choice_text = ""
        self.choice_values = []
        i = 0
        for ct, cv in choices:
            choice_text += _CHOICE_CHARS[i] + ") " + ct + "\n"
            self.choice_values.append(cv)
            i += 1
        self.choice_g = res.create_text_graphic(choice_text, 20, 50,
                                                max_width=w - 20)
        self.choice_count = i
        self.cancel_result = cancel_result

        # bind keys of input handler
        self.input_handler = InputHandler()
        for i in range(self.choice_count):
            v = self.choice_values[i]
            self.input_handler.add_handler(v, _CHOICE_KEYS[i])
        if cancel is True:
            self.input_handler.add_handler(self.cancel_result,
                                           sdl2.SDLK_ESCAPE)

    def choose(self):
        """Returns the value of the chosen Choice."""
        self.update()
        self.render()
        return self.input_handler.handle_event()

    def update(self):
        self.graphic.make_render_target()
        res.render_clear()
        self.header.render()
        self.choice_g.render()
        res.reset_render_target()

    def render(self):
        self.graphic.render()
        res.render_present()


# Test code
def _test():
    head = "Example Header."
    choices = ["Take this.", "Body Slam",
               "I don't know anymore."]
    m = ChoiceMenu(0, 0, 500, 500, head, choices)
    m.render()
    print("You chose Nr: %s" % m.choose())


if __name__ == "__main__":
    _test()

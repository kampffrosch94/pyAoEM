import res
import ecs
import components

class StartRenderSystem(ecs.System):
    def __init__(self):
        super().__init__([components.StartBuffer])
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

    def set_end_game(self,text):
        self.choice.destroy() #TODO remove on removal of destroy
        self.choice = res.create_text_graphic(
            text +
            "\n\nb) to quit",
            x=100, y=300)

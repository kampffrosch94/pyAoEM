"""Holds and Renders the Messagelog in battles."""
import res

messages = []

graphic = res.create_graphic(x=0, y=480, w=640, h=160)

dirty = False

def add_msg(msg):
    global dirty
    messages.append(msg)
    if len(messages) > 9:
        del messages[0]
    dirty = True

def update():
    global dirty
    if dirty:
        graphic.make_render_target()
        res.render_clear()
        y = 0
        for msg in messages:
            g = res.create_text_graphic(msg)
            g.y = y
            g.render()
            y += g.h
            g.destroy()
        res.reset_render_target()
        dirty = False

def render():
    update()
    graphic.render()

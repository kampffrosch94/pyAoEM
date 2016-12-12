import ecs
import menu
import res

_world = None  # type: ecs.World


def activate(world: ecs.World):
    global _world
    _world = world
    world.main_loop = main_loop


def main_loop():
    header = "You have %s gold." % _world.base.gold
    choices = ["More Gold please.", "Less Gold please.", "Quit."]
    m = menu.ChoiceMenu(200, 170, 200, 200, header, choices)
    res.render_clear()
    c = m.choose()
    if c == 0:
        _world.base.gold += 100
    elif c == 1:
        _world.base.gold -= 100
    elif c == 2:
        _world.end()

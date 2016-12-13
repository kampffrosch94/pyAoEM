import ecs
import menu
import res
import game

_world = None  # type: ecs.World


def activate(world: ecs.World):
    global _world
    _world = world
    world.main_loop = main_loop


def main_loop():
    pcs = _world.get_system_entities(game.TurnOrderSystem)
    header = "You have %s gold." % _world.base.gold
    choices = []
    choices.extend([(pc.name, lambda: None) for pc in pcs])
    m = menu.ChoiceMenu(200, 170, 200, 200, header, choices, cancel=True,
                        cancel_result=lambda: _world.end())
    res.render_clear()
    m.choose()()

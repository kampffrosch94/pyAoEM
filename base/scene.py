import ecs
import menu
import res
import game
import ability

_world = None  # type: ecs.World


def activate(world: ecs.World):
    global _world
    _world = world
    world.main_loop = main_loop


def do_at_cost(cost: int, action):
    if _world.base.gold >= cost:
        action()
        _world.base.gold -= cost


def ab_buy_loop(actor: ecs.Entity):
    header = "%s (You have %s gold.)" % (actor.name, _world.base.gold)

    abs = actor.get(game.Abilities)  # type: game.Abilities

    def add_ability(ab: ability.Ability):
        abs.add(ab)

    choices = [
        (a.name + " (%s g)" % a.unlock_cost,
         lambda x=a: do_at_cost(x.unlock_cost, lambda: add_ability(x)))
        for a in ability.abilities.values() if a not in abs.container
        ]

    def back():
        global current_loop
        current_loop = lambda: actor_loop(actor)

    m = menu.ChoiceMenu(150, 170, 400, 200, header, choices, cancel=True,
                        cancel_result=back)
    res.render_clear()
    m.choose()()


def actor_loop(actor: ecs.Entity):
    def inc_dmg():
        actor.get(game.Offensive).dmg += 1

    dmg = actor.get(game.Offensive).dmg

    def inc_hp():
        h = actor.get(game.Health)  # type: game.Health
        h.max_hp += 1
        h.hp += 1

    max_hp = actor.get(game.Health).max_hp

    def switch_to_ab_selection():
        global current_loop
        current_loop = lambda: ab_buy_loop(actor)

    header = "%s (You have %s gold.)" % (actor.name, _world.base.gold)
    choices = [
        ("Increase DMG for %sg: %s->%s" % (dmg * 100, dmg, dmg + 1),
         lambda: do_at_cost(dmg * 100, inc_dmg)),
        ("Increase HP for %sg: %s->%s" % (max_hp * 25, max_hp, max_hp + 1),
         lambda: do_at_cost(max_hp * 25, inc_hp)),
        ("Buy abilites.",
         switch_to_ab_selection),
    ]

    def back():
        global current_loop
        current_loop = start_loop

    m = menu.ChoiceMenu(150, 170, 400, 200, header, choices, cancel=True,
                        cancel_result=back)
    res.render_clear()
    m.choose()()


def start_loop():
    pcs = _world.get_system_entities(game.TurnOrderSystem)
    header = "You have %s gold." % _world.base.gold
    choices = []
    choices.extend([(pc.name, pc) for pc in pcs])
    m = menu.ChoiceMenu(200, 170, 200, 200, header, choices, cancel=True,
                        cancel_result=None)
    res.render_clear()
    chosen_actor = m.choose()
    if chosen_actor is not None:
        global current_loop
        current_loop = lambda: actor_loop(chosen_actor)
    else:
        _world.end()


# we exchange the loop depending on which menu we are in
current_loop = start_loop


def main_loop():
    current_loop()

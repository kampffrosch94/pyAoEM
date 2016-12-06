import time
from typing import Callable, Optional, List
import logging

import sdl2

import animation
import battle_log
import ecs
import game
import game_over
import input_
import map_
import menu
import movement
import res
import util

logger = logging.getLogger("Battle")

_world = None  # type: Optional[ecs.World]

# the canvas for the scene

canvas = res.create_graphic(0, 0, res.WINDOW_W, res.WINDOW_H)

# Components

controlled_entity = None


class Input(game.Component):
    """Component for Player controlled entities.
    Handles game.Act Events."""

    def __init__(self, entity):
        self.entity = entity
        self.priority = 0

    def act(self, _):
        global controlled_entity
        controlled_entity = self.entity
        while not input_.handle_event():
            pass


class BoundPosition:
    """The Position of the Entity witht this component is a copy of the Position
    this Component is attached to."""

    def __init__(self, attached_to: ecs.Entity):
        self.attached_to = attached_to
        self.priority = 0


# render code and System
def render_at_pos(graphic: res.Graphic, pos):
    if _world.map.is_visible(pos):
        graphic.x = map_.TILE_WIDTH * (pos.x - _world.map.root_pos.x)
        graphic.y = map_.TILE_HEIGHT * (pos.y - _world.map.root_pos.y)
        graphic.render()


def update_entity_graphic_pos(e):
    """Updates Graphic.(x,y) of an entity according to its position
    returns True if graphic is visible else False"""
    mp = e.get(util.Position)
    g = e.get(res.Graphic)
    return update_graphic_pos(g, mp)


def update_graphic_pos(g: res.Graphic, mp: util.Position):  # TODO move to map
    """Updates Graphic.(x,y) according to map_pos
    returns True if graphic is visible else False"""
    if _world.map.is_visible(mp):
        g.x = map_.TILE_WIDTH * (mp.x - _world.map.root_pos.x)
        g.y = map_.TILE_HEIGHT * (mp.y - _world.map.root_pos.y)
        return True
    return False


class BoundPositionSystem(ecs.System):
    def __init__(self):
        super().__init__([BoundPosition, util.Position])

    def process(self, entities: List[ecs.Entity]):
        for e in entities:
            binding = e.get(BoundPosition)  # type: BoundPosition
            bound_pos = binding.attached_to.get(util.Position)
            e.get(util.Position).update(bound_pos)


class EntityRenderSystem(ecs.System):
    """Renders enitities on the screen.
    Converts their MapPos into an appropriate Grapic.(x,y)"""

    def __init__(self):
        super().__init__([res.Graphic, util.Position])

    def process(self, entities):
        graphics = []
        for e in entities:
            if update_entity_graphic_pos(e):
                graphics.append(e.get(res.Graphic))

        z0 = [g for g in graphics if g.z == 0]
        z1 = [g for g in graphics if g.z == 1]
        for g in z0:
            g.render()
        for g in z1:
            g.render()


class HealthRenderSystem(ecs.System):
    """Renders the health of actors on the screen."""

    def __init__(self, world: ecs.World):
        super().__init__(
            [res.Graphic, util.Position, game.Health, game.Fatigue])
        self._world = world

    def process(self, entities: List[ecs.Entity]):
        _map = self._world.map
        for e in entities:
            mp = e.get(util.Position)
            if _map.is_visible(mp):
                hc = e.get(game.Health)
                g = e.get(res.Graphic)
                if hc.hp < hc.max_hp:
                    if hc.hp <= hc.max_hp / 5:
                        g.render_other_texture("dmg_almost_dead")
                    elif hc.hp <= hc.max_hp * 2 / 5:
                        g.render_other_texture("dmg_severely")
                    elif hc.hp <= hc.max_hp * 3 / 5:
                        g.render_other_texture("dmg_heavy")
                    elif hc.hp <= hc.max_hp * 4 / 5:
                        g.render_other_texture("dmg_moderate")
                    else:
                        g.render_other_texture("dmg_light")


def render_turn_order(es_in_to: List[ecs.Entity]):
    """render_entities must be run before this to update graphic positions"""
    # place green cursor around controlled pc
    current_actor = es_in_to[0]
    if _world.map.is_visible(current_actor.get(util.Position)):
        if current_actor.get(game.Team).team_name == "player_team":
            g = current_actor.get(res.Graphic)
            g.render_other_texture("cursor_green")

    # TODO cache turnorder graphic
    for i in range(1, min(len(es_in_to), 10)):  # next 9 in turnorder
        actor = es_in_to[i]
        if _world.map.is_visible(actor.get(util.Position)):
            g = actor.get(res.Graphic)  # type: res.Graphic
            tg = res.create_text_graphic(str(i))
            tg.x, tg.y = g.x, g.y
            tg.render()
            tg.destroy()


def render_animation(ani: animation.Animation):
    for pos in ani.positions:
        update_graphic_pos(ani.graphic, pos)
        ani.graphic.render()


def update():
    world = _world  # type: ecs.World

    world.map.update()
    battle_log.update()

    canvas.make_render_target()

    res.render_clear()
    world.map.render()
    battle_log.render()

    world.invoke_system(BoundPositionSystem)
    world.invoke_system(EntityRenderSystem)
    world.invoke_system(HealthRenderSystem)
    render_turn_order(world.get_system_entities(game.TurnOrderSystem))

    res.render_present()

    res.reset_render_target()

    canvas.render()
    res.render_present()  # TODO: might be wrong usage


def render():
    canvas.render()
    res.render_present()


# Keybindings

def entity_move_and_pay_fatigue(e: ecs.Entity, d):
    result = movement.attack_or_move(e, d)
    if result:
        e.handle_event(game.PayFatigue(100))
    return result


def player_move_dir_f(x, y):
    d = util.Direction(x, y)
    # lazy evaluation of controlled_entity
    return lambda: entity_move_and_pay_fatigue(controlled_entity, d)


def map_move_dir_f(x, y):
    def f():
        _world.map.root_pos.move(util.Direction(x, y))
        render()

    return f


def wait():
    controlled_entity.handle_event(game.PayFatigue(100))
    return True


# Sub_scenes

def cursor(target_f: Optional[Callable] = None,
           relevant_entities: Optional[ecs.Entity] = None,
           max_range=float("inf")) -> util.Position:
    """returns Position selected with the cursor or None if cancelled"""
    start = controlled_entity.get(util.Position)  # type: util.Position
    pos = start.copy()
    g = res.load_graphic("cursor")

    trail_g = res.load_graphic("ray")

    def move_dir_f(x, y):
        def move():
            if start.distance(pos.copy().move(
                    util.Direction(x, y))) <= max_range:
                pos.move(util.Direction(x, y))

        return move

    def stop_with_target():
        return False

    def cancel():
        return True

    input_.clear_handlers()
    input_.add_handler(cancel, sdl2.SDLK_ESCAPE)
    input_.add_handler(stop_with_target, sdl2.SDLK_RETURN)
    input_.add_handler(move_dir_f(-1, 0), sdl2.SDLK_h)
    input_.add_handler(move_dir_f(+1, 0), sdl2.SDLK_l)
    input_.add_handler(move_dir_f(0, -1), sdl2.SDLK_k)
    input_.add_handler(move_dir_f(0, +1), sdl2.SDLK_j)
    input_.add_handler(move_dir_f(+1, -1), sdl2.SDLK_u)
    input_.add_handler(move_dir_f(+1, +1), sdl2.SDLK_n)
    input_.add_handler(move_dir_f(-1, -1), sdl2.SDLK_z)
    input_.add_handler(move_dir_f(-1, +1), sdl2.SDLK_b)

    is_cancelled = None
    while is_cancelled is None:
        render()
        render_at_pos(g, pos)

        if target_f is not None:
            for p in target_f(_world.map,
                              relevant_entities,
                              start,
                              pos):
                render_at_pos(trail_g, p)

        res.render_present()
        is_cancelled = input_.handle_event()

    render()
    bind_keys()

    if is_cancelled:
        return None
    else:
        return pos


def look():
    pos = cursor()
    if pos is None:
        return
    print("Endpos is: %s" % pos)
    for e in _world.entities:
        if e.has(util.Position):
            if e.get(util.Position) == pos:
                print(str(e))


def choose_ability():
    m_head = "Abilities."
    # TODO use abilities of current actor
    abilities = controlled_entity.get(game.Abilities).container
    m_choices = [a.name for a in abilities]
    m = menu.ChoiceMenu(200, 150, 300, 200, m_head, m_choices, cancel=True)
    choice = m.choose()
    bind_keys()
    render()
    if choice is None:
        return False  # dont end turn if selection was cancelled
    ab = abilities[choice]

    actors = _world.get_system_entities(game.TurnOrderSystem)
    target_pos = cursor(ab.target, actors, ab.range_)
    if target_pos is None:
        return False  # dont end turn if cursor() was cancelled
    current_actor = actors[0]

    ab.fire(_world.map, actors, current_actor, target_pos)
    render()
    return True  # end turn after using ability


# Debug keybindings
def regen_map():
    map_w, map_h = 20, 15
    wall_chance = 42
    _world.map = map_.TileMap(map_w, map_h, wall_chance)
    render()


def quit_():
    input_.quit_handler()
    return True


def go_interpreter():
    actors = _world.get_system_entities(game.TurnOrderSystem)

    # noinspection PyUnusedLocal
    def print_actors():
        import functools

        def concat(x, y):
            return x + "\n" + y

        print(str(functools.reduce(concat, map(str, actors))))

    import IPython
    IPython.embed()


# Activation

def bind_keys():
    input_.clear_handlers()

    input_.add_handler(quit_, sdl2.SDLK_q)
    input_.add_handler(go_interpreter, sdl2.SDLK_y)

    input_.add_handler(map_move_dir_f(-1, 0), sdl2.SDLK_h, sdl2.KMOD_SHIFT)
    input_.add_handler(map_move_dir_f(+1, 0), sdl2.SDLK_l, sdl2.KMOD_SHIFT)
    input_.add_handler(map_move_dir_f(0, -1), sdl2.SDLK_k, sdl2.KMOD_SHIFT)
    input_.add_handler(map_move_dir_f(0, +1), sdl2.SDLK_j, sdl2.KMOD_SHIFT)

    input_.add_handler(regen_map, sdl2.SDLK_F1)

    input_.add_handler(player_move_dir_f(-1, 0), sdl2.SDLK_h)
    input_.add_handler(player_move_dir_f(+1, 0), sdl2.SDLK_l)
    input_.add_handler(player_move_dir_f(0, -1), sdl2.SDLK_k)
    input_.add_handler(player_move_dir_f(0, +1), sdl2.SDLK_j)
    input_.add_handler(player_move_dir_f(+1, -1), sdl2.SDLK_u)
    input_.add_handler(player_move_dir_f(+1, +1), sdl2.SDLK_n)
    input_.add_handler(player_move_dir_f(-1, -1), sdl2.SDLK_z)
    input_.add_handler(player_move_dir_f(-1, +1), sdl2.SDLK_b)
    input_.add_handler(wait, sdl2.SDLK_PERIOD)
    input_.add_handler(look, sdl2.SDLK_COMMA)

    input_.add_handler(choose_ability, sdl2.SDLK_a)


def activate(world):
    global _world
    _world = world
    world.main_loop = main_loop
    bind_keys()


def main_loop():
    logger.debug("Enter main_loop")
    if len(_world.animation_q) > 0:
        canvas.make_render_target()
        for ani in _world.animation_q:
            render_animation(ani)
        res.reset_render_target()
        render()
        time.sleep(0.3)
        _world.animation_q.clear()
        update()
        render()
    else:
        update()
        render()
    game.active_take_turn(_world)

    # check game over
    entities = _world.get_system_entities(game.TurnOrderSystem)
    if all(entities[0].get(game.Team) == e.get(game.Team) for e in entities):
        game_over.activate(
            entities[0].get(game.Team).team_name == "player_team")

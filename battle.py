import enum
import logging
import time
from typing import Callable, Optional, List

import sdl2

import ability
import ability.ability
import action
import animation
import base.scene
import battle_log
import ecs
import factory
import game
import game_over
import map_
import menu
import movement
import res
import util
from game import BoundPositionSystem
from input_ import InputHandler

logger = logging.getLogger("Battle")

_world = None  # type: Optional[ecs.World]

# the canvas for the scene

canvas = res.create_graphic(0, 0, res.WINDOW_W, res.WINDOW_H)

# Components

controlled_entity = None  # type: Optional[ecs.Entity]


class Input(game.Component):
    """Component for Player controlled entities.
    Handles game.Act Events."""

    def __init__(self, entity):
        self.entity = entity
        self.priority = 0
        self.handler = Input.create_key_handler(entity)

    def act(self, _):
        global controlled_entity
        controlled_entity = self.entity
        while not self.handler.handle_event()():
            pass

    @staticmethod
    def create_key_handler(entity):
        handler = InputHandler()
        handler.add_handler(quit_, sdl2.SDLK_q)
        handler.add_handler(go_interpreter, sdl2.SDLK_y)

        handler.add_handler(map_move_dir_f(-1, 0), sdl2.SDLK_h,
                            sdl2.KMOD_SHIFT)
        handler.add_handler(map_move_dir_f(+1, 0), sdl2.SDLK_l,
                            sdl2.KMOD_SHIFT)
        handler.add_handler(map_move_dir_f(0, -1), sdl2.SDLK_k,
                            sdl2.KMOD_SHIFT)
        handler.add_handler(map_move_dir_f(0, +1), sdl2.SDLK_j,
                            sdl2.KMOD_SHIFT)

        handler.add_handler(regen_map, sdl2.SDLK_F1)

        handler.add_handler(player_move_dir_f(-1, 0), sdl2.SDLK_h)
        handler.add_handler(player_move_dir_f(+1, 0), sdl2.SDLK_l)
        handler.add_handler(player_move_dir_f(0, -1), sdl2.SDLK_k)
        handler.add_handler(player_move_dir_f(0, +1), sdl2.SDLK_j)
        handler.add_handler(player_move_dir_f(+1, -1), sdl2.SDLK_u)
        handler.add_handler(player_move_dir_f(+1, +1), sdl2.SDLK_n)
        handler.add_handler(player_move_dir_f(-1, -1), sdl2.SDLK_z)
        handler.add_handler(player_move_dir_f(-1, +1), sdl2.SDLK_b)
        handler.add_handler(wait, sdl2.SDLK_PERIOD)
        handler.add_handler(look, sdl2.SDLK_COMMA)

        handler.add_handler(lambda e=entity: choose_ability(e), sdl2.SDLK_a)
        return handler


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
        update()
        render()

    return f


def wait():
    controlled_entity.handle_event(game.PayFatigue(100))
    return True


# Sub_scenes

def cursor(target_f: Optional[Callable] = None,
           relevant_entities: Optional[List[ecs.Entity]] = None,
           max_range=float("inf")) -> Optional[util.Position]:
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

    cursor_handler = InputHandler()
    cursor_handler.add_handler(cancel, sdl2.SDLK_ESCAPE)
    cursor_handler.add_handler(stop_with_target, sdl2.SDLK_RETURN)
    cursor_handler.add_handler(move_dir_f(-1, 0), sdl2.SDLK_h)
    cursor_handler.add_handler(move_dir_f(+1, 0), sdl2.SDLK_l)
    cursor_handler.add_handler(move_dir_f(0, -1), sdl2.SDLK_k)
    cursor_handler.add_handler(move_dir_f(0, +1), sdl2.SDLK_j)
    cursor_handler.add_handler(move_dir_f(+1, -1), sdl2.SDLK_u)
    cursor_handler.add_handler(move_dir_f(+1, +1), sdl2.SDLK_n)
    cursor_handler.add_handler(move_dir_f(-1, -1), sdl2.SDLK_z)
    cursor_handler.add_handler(move_dir_f(-1, +1), sdl2.SDLK_b)

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
        is_cancelled = cursor_handler.handle_event()()

    render()

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


def choose_ability(user):
    m_head = "Abilities."
    abilities = user.get(ability.ability.Abilities).container
    if len(abilities) < 1:
        return
    m_choices = [(a.name, a) for a in abilities]
    m = menu.ChoiceMenu(200, 150, 300, 200, m_head, m_choices, cancel=True)
    choice = m.choose()
    render()
    if choice is None:
        return False  # dont end turn if selection was cancelled
    ab = choice

    actors = _world.get_system_entities(game.TurnOrderSystem)
    target_pos = cursor(ab.target, actors, ab.range_)
    if target_pos is None:
        return False  # dont end turn if cursor() was cancelled
    act = action.StandardAction(controlled_entity, ab, target_pos)
    act.execute()
    render()
    return True  # end turn after using ability


# Debug keybindings
def regen_map():
    _world.map.regen()
    update()
    render()


def quit_():
    _world.end()
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

def separate_teams():
    """Playerchars to the left, rest to the right"""
    world = _world
    actors = world.find_entities_with_components([game.Team])
    pcs = [a for a in actors if a.get(game.Team).team_name == "player_team"]
    enemies = [a for a in actors if a.get(game.Team).team_name != "player_team"]
    pos_list = [x for x in world.map.wall_map]
    pos_list.sort(key=(lambda p: p[0] * world.map.w + p[1]))
    for pos in pos_list:
        if len(pcs) == 0:
            break
        if movement.pos_is_free(world, pos):
            e = pcs.pop()
            mp = e.get(util.Position)
            mp.x, mp.y = pos
    pos_list.reverse()
    for pos in pos_list:
        if len(enemies) == 0:
            break
        if movement.pos_is_free(world, pos):
            e = enemies.pop()
            mp = e.get(util.Position)
            mp.x, mp.y = pos


def after_battle_cleanup():
    """Battle is finished -> clean up blood, corpses & heal injuries."""
    deads = _world.find_entities_with_components([game.DeadTag])
    for dead in deads:
        # clean up inventory
        if dead.has(game.Inventory):
            i = dead.get(game.Inventory)  # type: game.Inventory
            for item in i.items:
                item.remove()
        # delete the dead guy
        dead.remove()

    # heal the battered and bruised
    healables = _world.find_entities_with_components([game.Health])
    for e in healables:
        h = e.get(game.Health)  # type: game.Health
        h.hp = h.max_hp

    # reset fatigue
    fatigued = _world.find_entities_with_components([game.Fatigue])
    for e in fatigued:
        f = e.get(game.Fatigue)  # type: game.Fatigue
        f.value = 0


def activate(world: ecs.World):
    global _world
    _world = world
    world.main_loop = main_loop
    world.map.regen()

    for i in range(5):
        c = factory.create_ai_creature(
            name="giant newt idler",
            texture="newt",
            pos=(5, 5),
            mhp=5,
            dmg=2)
        abe = c.get(ability.ability.Abilities)
        abe.add(ability.abilities["rush"])
    separate_teams()


class BattleStatus(enum.Enum):
    not_finished = 1
    won = 2
    lost = 3


def check_battle_status(world: ecs.World) -> BattleStatus:
    actors = world.get_system_entities(game.TurnOrderSystem)
    # all actors are on the same team -> battle finished
    if all(actors[0].get(game.Team) == e.get(game.Team) for e in actors):
        won = actors[0].get(game.Team).team_name == "player_team"
        if won:
            return BattleStatus.won
        else:
            return BattleStatus.lost

    return BattleStatus.not_finished


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
        # check game over
        status = check_battle_status(_world)
        if status is BattleStatus.lost:
            game_over.activate(_world)
        elif status is BattleStatus.won:
            _world.invoke_system(game.LootSystem)
            after_battle_cleanup()
            base.scene.activate(_world)
        elif status is BattleStatus.not_finished:
            update()
            render()
            game.active_take_turn(_world)

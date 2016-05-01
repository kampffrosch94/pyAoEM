import sdl2

import ability
import battle_log
import ecs
import game
import input_
import map_
import menu
import movement
import res
import utility

# the canvas for the scene

canvas = res.create_graphic(0, 0, res.WINDOW_W, res.WINDOW_H)

# Components

controlled_entity = None


class Input(object):
    """Component for Player controlled entities."""

    def __init__(self, entity):
        self.entity = entity
        self.priority = 0

    def act(self, event):
        global controlled_entity
        controlled_entity = self.entity
        while not input_.handle_event():
            pass


# render code and System
def render_at_pos(graphic: res.Graphic, pos):
    if map_.current_map.is_visible(pos):
        graphic.x = map_.TILE_WIDTH * (pos.x - map_.current_map.root_pos.x)
        graphic.y = map_.TILE_HEIGHT * (pos.y - map_.current_map.root_pos.y)
        graphic.render()


def update_graphic_pos(e):
    """returns True if graphic is visible else False"""
    mp = e.get(game.MapPos)
    if map_.current_map.is_visible(mp):
        g = e.get(res.Graphic)
        g.x = map_.TILE_WIDTH * (mp.x - map_.current_map.root_pos.x)
        g.y = map_.TILE_HEIGHT * (mp.y - map_.current_map.root_pos.y)
        return True
    return False


class EntityRenderSystem(ecs.System):
    def __init__(self):
        super().__init__([res.Graphic, game.MapPos])

    def process(self, entities):
        graphics = []
        for e in entities:
            if update_graphic_pos(e):
                graphics.append(e.get(res.Graphic))

        z0 = [g for g in graphics if g.z == 0]
        z1 = [g for g in graphics if g.z == 1]
        for g in z0:
            g.render()
        for g in z1:
            g.render()


class HealthRenderSystem(ecs.System):
    def __init__(self):
        super().__init__([res.Graphic, game.MapPos, game.Health, game.Fatigue])

    def process(self, entities):
        for e in entities:
            mp = e.get(game.MapPos)
            if map_.current_map.is_visible(mp):
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


def render_turn_order(es_in_to):
    """render_entities must be run before this to update graphic positions"""
    current_actor = es_in_to[0]
    if map_.current_map.is_visible(current_actor.get(game.MapPos)):
        if current_actor.get(game.Team).team_name == "player_team":
            g = current_actor.get(res.Graphic)
            g.render_other_texture("cursor_green")


def render():
    world = _world

    map_.current_map.update()
    battle_log.update()

    canvas.make_render_target()

    res.render_clear()
    map_.current_map.render()
    battle_log.render()

    world.invoke_system(EntityRenderSystem)
    world.invoke_system(HealthRenderSystem)
    render_turn_order(world.get_system_entities(game.TurnOrderSystem))

    res.render_present()

    res.reset_render_target()

    canvas.render()
    res.render_present()


# Keybindings


def player_move_dir_f(x, y):
    d = utility.Direction(x, y)
    return lambda: movement.attack_or_move(controlled_entity, d)


def map_move_dir_f(x, y):
    def f():
        map_.current_map.root_pos.apply_direction(utility.Direction(x, y))
        render()

    return f


def wait():
    controlled_entity.handle_event(game.PayFatigue(100))
    return True


# Sub_scenes

def cursor(target_f=None):
    start = controlled_entity.get(game.MapPos)
    pos = start.copy()
    g = res.load_graphic("cursor")

    trail_g = res.load_graphic("ray")

    def move_dir_f(x, y):
        return lambda: pos.apply_direction(utility.Direction(x, y))

    def stop():
        return True

    input_.clear_handlers()
    input_.add_handler(stop, sdl2.SDLK_ESCAPE)
    input_.add_handler(stop, sdl2.SDLK_RETURN)
    input_.add_handler(move_dir_f(-1, 0), sdl2.SDLK_h)
    input_.add_handler(move_dir_f(+1, 0), sdl2.SDLK_l)
    input_.add_handler(move_dir_f(0, -1), sdl2.SDLK_k)
    input_.add_handler(move_dir_f(0, +1), sdl2.SDLK_j)
    input_.add_handler(move_dir_f(+1, -1), sdl2.SDLK_u)
    input_.add_handler(move_dir_f(+1, +1), sdl2.SDLK_n)
    input_.add_handler(move_dir_f(-1, -1), sdl2.SDLK_z)
    input_.add_handler(move_dir_f(-1, +1), sdl2.SDLK_b)
    render_at_pos(g, pos)
    res.render_present()

    while not input_.handle_event():
        render()
        render_at_pos(g, pos)

        if target_f is not None:
            for p in target_f(map_.current_map, start.to_tuple(),
                              pos.to_tuple()):
                render_at_pos(trail_g, utility.Position(p[0], p[1]))

        res.render_present()

    render()
    bind_keys()

    return pos


def look():
    pos = cursor()
    print("Endpos is: %s" % pos)
    for e in _world.entities:
        if e.has(game.MapPos):
            if e.get(game.MapPos) == pos:
                print(str(e))


def choose_ability():
    m_head = "Abilities."
    m_choices = list(ability.abilities.keys())
    m = menu.ChoiceMenu(200, 150, 300, 200, m_head, m_choices)
    choice = m.choose()
    ab = ability.abilities[m_choices[choice]]
    bind_keys()
    render()

    target_pos = cursor(ab.target);
    actors = _world.get_system_entities(game.TurnOrderSystem)
    ab.fire(map_.current_map, actors, actors[0], target_pos)
    render()

    # debug info TODO remove this when done
    # target = None
    # for e in actors:
    #    if e.get(game.MapPos) == target_pos: 
    #        target = e
    # if target is not None:
    #    print("Target is: \n %s" % target)
    # else:
    #    print("No target at %s" % target_pos)


# Debug keybindings
def regen_map():
    map_w, map_h = 20, 15
    wall_chance = 42
    map_.current_map = map_.TileMap(map_w, map_h, wall_chance)
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

    import IPython;
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


_world = None


def activate(world):
    global _world
    _world = world
    world.main_loop = main_loop
    bind_keys()


def main_loop():
    _world.invoke_system(game.TurnOrderSystem)
    render()
    game.active_take_turn(_world.get_system_entities(game.TurnOrderSystem))

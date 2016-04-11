import sdl2
import res
import input_
import ecs
import map_
import game
import movement
import utility
import battle_log

# the canvas for the scene

canvas = res.create_graphic(0,0,res.WINDOW_W,res.WINDOW_H)

# Components

controlled_entity = None

class Input(object):
    """Component for Player controlled entities."""
    def __init__(self,entity):
        self.entity = entity
        self.priority = 0

    def act(self,event):
        global controlled_entity
        controlled_entity = self.entity
        while not input_.handle_event():
            pass

# render code and System

def update_graphic_pos(e):
    """returns True if graphic is visible else False"""
    mp = e.get(game.MapPos)
    if map_.current_map.is_visible(mp):
        g = e.get(res.Graphic)
        g.x = map_.TILE_WIDTH * (mp.x - map_.current_map.root_pos.x)
        g.y = map_.TILE_HEIGHT*(mp.y - map_.current_map.root_pos.y)
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

# Input for a controlled entity on the map

def move_right():
    d = utility.Direction(1,0)
    return movement.attack_or_move(controlled_entity,d)

def move_left():
    d = utility.Direction(-1,0)
    return movement.attack_or_move(controlled_entity,d)

def move_up():
    d = utility.Direction(0,-1)
    return movement.attack_or_move(controlled_entity,d)

def move_down():
    d = utility.Direction(0,1)
    return movement.attack_or_move(controlled_entity,d)

def move_right_up():
    d = utility.Direction(1,-1)
    return movement.attack_or_move(controlled_entity,d)

def move_right_down():
    d = utility.Direction(1,1)
    return movement.attack_or_move(controlled_entity,d)

def move_left_up():
    d = utility.Direction(-1,-1)
    return movement.attack_or_move(controlled_entity,d)

def move_left_down():
    d = utility.Direction(-1,1)
    return movement.attack_or_move(controlled_entity,d)

def wait():
    controlled_entity.handle_event(game.PayFatigue(100))
    return True

# Input for moving the map_view

map_w,map_h = 20,15
wall_chance = 42
def regen_map():
    map_.current_map = map_.TileMap(map_w,map_h,wall_chance)
    render()
def map_left():
    map_.current_map.root_pos.x -= 1
    render()
def map_right():
    map_.current_map.root_pos.x += 1
    render()
def map_up():
    map_.current_map.root_pos.y -= 1
    render()
def map_down():
    map_.current_map.root_pos.y += 1
    render()
def quit_():
    input_.quit_handler()
    return True
def go_interpreter():
    import IPython; IPython.embed()

# Activation

def bind_keys():
    input_.clear_handlers()

    input_.add_handler(quit_, sdl2.SDLK_q)
    input_.add_handler(go_interpreter,sdl2.SDLK_y)

    input_.add_handler(map_right,sdl2.SDLK_l,sdl2.KMOD_SHIFT)
    input_.add_handler(map_left ,sdl2.SDLK_h,sdl2.KMOD_SHIFT)
    input_.add_handler(map_up   ,sdl2.SDLK_k,sdl2.KMOD_SHIFT)
    input_.add_handler(map_down ,sdl2.SDLK_j,sdl2.KMOD_SHIFT)

    input_.add_handler(regen_map,sdl2.SDLK_F1)

    input_.add_handler(move_right,      sdl2.SDLK_l)
    input_.add_handler(move_left,       sdl2.SDLK_h)
    input_.add_handler(move_up,         sdl2.SDLK_k)
    input_.add_handler(move_down,       sdl2.SDLK_j)
    input_.add_handler(move_right_up,   sdl2.SDLK_u)
    input_.add_handler(move_right_down, sdl2.SDLK_n)
    input_.add_handler(move_left_up,    sdl2.SDLK_z)
    input_.add_handler(move_left_down,  sdl2.SDLK_b)
    input_.add_handler(wait,            sdl2.SDLK_PERIOD)

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

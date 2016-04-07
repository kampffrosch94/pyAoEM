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

class BattleBuffer(object):
    pass

controlled_entity = None

class Input(object):
    """Component for Player controlled entities."""
    def __init__(self,entity):
        self.entity = entity
        self.priority = 0

    def act(self,event):
        global controlled_entity
        controlled_entity = self.entity
        input_.handle_event()

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


class BattleRenderSystem(ecs.System):
    def __init__(self,turn_order_system):
        super().__init__([res.Graphic, game.MapPos, BattleBuffer])
        self.turn_order_system = turn_order_system

    def render_entities(self,entities):
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

    def render_turn_order(self, es_in_to):
        """render_entities must be run before to update graphic positions"""
        current_actor = es_in_to[0]
        if current_actor.get(game.Team).team_name == "player_team":
            g = current_actor.get(res.Graphic)
            g.render_other_texture("cursor_green")

    def process(self,entities):
        map_.current_map.update()
        battle_log.update()

        canvas.make_render_target()

        res.render_clear()
        map_.current_map.render()
        battle_log.render()
        self.render_entities(entities)
        self.render_turn_order(self.turn_order_system.turn_order)
        res.render_present()

        res.reset_render_target()

        canvas.render()
        res.render_present()


turn_order_system = game.TurnOrderSystem()

system = BattleRenderSystem(turn_order_system)

act_system = game.ActSystem(turn_order_system)

# Activation

def activate():
    system.active = True
    turn_order_system.active = True
    act_system.active = True
    input_.activate_mode(BattleMode)

def deactivate():
    system.active = False
    turn_order_system.active = False
    act_system.active = False

# Keybinds

class BattleMode():
    pass

# Input for a controlled entity on the map

def move_right():
    d = utility.Direction(1,0)
    movement.attack_or_move(controlled_entity,d)

def move_left():
    d = utility.Direction(-1,0)
    movement.attack_or_move(controlled_entity,d)

def move_up():
    d = utility.Direction(0,-1)
    movement.attack_or_move(controlled_entity,d)

def move_down():
    d = utility.Direction(0,1)
    movement.attack_or_move(controlled_entity,d)

def move_right_up():
    d = utility.Direction(1,-1)
    movement.attack_or_move(controlled_entity,d)

def move_right_down():
    d = utility.Direction(1,1)
    movement.attack_or_move(controlled_entity,d)

def move_left_up():
    d = utility.Direction(-1,-1)
    movement.attack_or_move(controlled_entity,d)

def move_left_down():
    d = utility.Direction(-1,1)
    movement.attack_or_move(controlled_entity,d)

def wait():
    controlled_entity.handle_event(game.PayFatigue(100))

input_.add_handler(BattleMode, move_right,      sdl2.SDLK_l)
input_.add_handler(BattleMode, move_left,       sdl2.SDLK_h)
input_.add_handler(BattleMode, move_up,         sdl2.SDLK_k)
input_.add_handler(BattleMode, move_down,       sdl2.SDLK_j)
input_.add_handler(BattleMode, move_right_up,   sdl2.SDLK_u)
input_.add_handler(BattleMode, move_right_down, sdl2.SDLK_n)
input_.add_handler(BattleMode, move_left_up,    sdl2.SDLK_z)
input_.add_handler(BattleMode, move_left_down,  sdl2.SDLK_b)
input_.add_handler(BattleMode, wait,            sdl2.SDLK_PERIOD)

# Input for moving the map_view

map_w,map_h = 20,15
wall_chance = 42
def regen_map():
    map_.current_map = map_.TileMap(map_w,map_h,wall_chance)
def map_left():
    map_.current_map.root_pos.x -= 1
def map_right():
    map_.current_map.root_pos.x += 1
def map_up():
    map_.current_map.root_pos.y -= 1
def map_down():
    map_.current_map.root_pos.y += 1

input_.add_handler(BattleMode,map_right,sdl2.SDLK_l,sdl2.KMOD_SHIFT)
input_.add_handler(BattleMode,map_left ,sdl2.SDLK_h,sdl2.KMOD_SHIFT)
input_.add_handler(BattleMode,map_up   ,sdl2.SDLK_k,sdl2.KMOD_SHIFT)
input_.add_handler(BattleMode,map_down ,sdl2.SDLK_j,sdl2.KMOD_SHIFT)
input_.add_handler(BattleMode,regen_map,sdl2.SDLK_F1)

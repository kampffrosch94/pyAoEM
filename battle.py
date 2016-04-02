import sdl2
import res
import input_
import ecs
import map_
import game
import movement
import utility
import battle_log

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

# System

class BattleRenderSystem(ecs.System):
    def __init__(self):
        super().__init__([res.Graphic, game.MapPos, BattleBuffer])

    def render_entities(self,entities):
        graphics = []
        for e in entities:
            mp = e.get(game.MapPos)
            if map_.current_map.is_visible(mp):
                g = e.get(res.Graphic)
                g.x = map_.TILE_WIDTH * (mp.x - map_.current_map.root_pos.x)
                g.y = map_.TILE_HEIGHT *(mp.y - map_.current_map.root_pos.y)
                graphics.append(g)

        z0 = [g for g in graphics if g.z == 0]
        z1 = [g for g in graphics if g.z == 1]
        for g in z0:
            g.render()
        for g in z1:
            g.render()

    def process(self,entities):
        res.render_clear()
        map_.current_map.render()
        self.render_entities(entities)
        battle_log.render()
        res.render_present()

system = BattleRenderSystem()

class ActRenderSystem(ecs.System):
    def __init__(self):
        ecs.System.__init__(self,[game.Act,game.Team,res.Graphic])
        self.cursor = res.load_graphic("cursor_green")

    def process(self,entities):
        assert len(entities) == 1
        e = entities[0]
        act = e.get(game.Act)
        e.delete(game.Act)
        g = e.get(res.Graphic)
        if e.get(game.Team).team_name == "player_team":
            self.cursor.x = g.x
            self.cursor.y = g.y
            self.cursor.render()
            res.render_present()
        e.handle_event(act)

act_system = ActRenderSystem()

turnorder_system = game.TurnOrderSystem()
# Activation

def activate():
    system.active = True
    act_system.active = True
    turnorder_system.active = True
    input_.activate_mode(BattleMode)

def deactivate():
    system.active = False
    act_system.active = False
    turnorder_system.active = False

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

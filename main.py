from sdl2 import *
from sdl2.sdlimage import *
from ecs import World,Entity 
from systems import *
from components import *
from errors import SDL_Exception
from utility import Position
import sdl_manager
import input_manager
import map_manager
from map_manager import TileMap
import movement
from utility import Direction

world = World()

maptographicsystem = MapToGraphicSystem(world)
world.add_system(maptographicsystem)

battlerendersystem = BattleRenderSystem()
world.add_system(battlerendersystem)

startrendersystem = StartRenderSystem()
startrendersystem.active = False
world.add_system(startrendersystem)

def switch_buffer():
    battlerendersystem.active = not battlerendersystem.active
    startrendersystem.active  = not startrendersystem.active

inputsystem = InputSystem()
world.add_system(inputsystem)

worldstepsystem = WorldStepSystem(world,[
    maptographicsystem,
    startrendersystem,
    battlerendersystem,
    inputsystem])
world.add_system(worldstepsystem)

###Gamesystems
world.add_system(BlockingSystem())
world.add_system(AttackableSystem())
###Gamesystems end

player_char = Entity(world)
player_char.name = "Player"
texture = sdl_manager.load_texture("human_m")
player_char.set(Graphic(texture))
player_char.set(BattleBuffer())
player_char.set(MapPos(1,1))
player_char.set(Health(player_char,10))
player_char.set(Blocking())
player_char.set(Offensive(dmg=2))

enemy = Entity(world)
texture = sdl_manager.load_texture("newt")
enemy.name = "giant newt"
enemy.set(Graphic(texture))
enemy.set(BattleBuffer())
enemy.set(MapPos(5,5))
enemy.set(Health(enemy,5))
enemy.set(Blocking())
corpsetexture = sdl_manager.load_texture("blood0")
enemy.set(CorpseGraphic(corpsetexture))

texturepath = "cobble_blood1"
default_texture = sdl_manager.load_texture(texturepath)

map_manager.current_map = TileMap(1000,1000,default_texture)

from map_manager import current_map as tmap
def map_left():
    tmap.root_pos.x -= 1
def map_right():
    tmap.root_pos.x += 1
def map_up():
    tmap.root_pos.y -= 1
def map_down():
    tmap.root_pos.y += 1
def end_world():
    world.end()
def delete_test():
    player_char.delete(Graphic)

from movement import can_move, move, can_bump_attack,bump_attack
def attack_or_move(entity,direction):
    if can_move(entity,direction):
        move(entity,direction)
    elif can_bump_attack(entity,direction):
        bump_attack(entity,direction)

def move_right():
    d = Direction(1,0)
    attack_or_move(player_char,d)
def move_left():
    d = Direction(-1,0)
    attack_or_move(player_char,d)
def move_up():
    d = Direction(0,-1)
    attack_or_move(player_char,d)
def move_down():
    d = Direction(0,1)
    attack_or_move(player_char,d)

def go_interpreter():
    e = player_char
    import IPython; IPython.embed()

from input_manager import BattleMode
input_manager.quit_handler = end_world

input_manager.add_handler(BattleMode,move_right,SDLK_l)
input_manager.add_handler(BattleMode,move_left,SDLK_h)
input_manager.add_handler(BattleMode,move_up  ,SDLK_k)
input_manager.add_handler(BattleMode,move_down,SDLK_j)
                                                      
input_manager.add_handler(BattleMode,map_right,SDLK_l,KMOD_SHIFT)
input_manager.add_handler(BattleMode,map_left ,SDLK_h,KMOD_SHIFT)
input_manager.add_handler(BattleMode,map_up   ,SDLK_k,KMOD_SHIFT)
input_manager.add_handler(BattleMode,map_down ,SDLK_j,KMOD_SHIFT)
input_manager.add_handler(BattleMode,end_world,SDLK_q)
input_manager.add_handler(BattleMode,delete_test,SDLK_x)
input_manager.add_handler(BattleMode,switch_buffer,SDLK_t)
input_manager.add_handler(BattleMode,go_interpreter,SDLK_y)
input_manager.activate_mode(BattleMode)

def main():
    battle_log.add_msg("Welcome to AoEM.")
    while world.alive:
        world.invoke_system(WorldStepSystem)
    
    world.destroy()

if __name__ == "__main__":
    main()

from sdl2 import *
from sdl2.sdlimage import *
from ecs import World,Entity 
from systems import *
from components import *
from errors import SDL_Exception
import sdl_manager
import input_manager
import map_manager
from map_manager import TileMap
import movement
from utility import Direction
import pc_control
import factory

world = World()

maptographicsystem = MapToGraphicSystem(world)
world.add_system(maptographicsystem)

battlerendersystem = BattleRenderSystem()
world.add_system(battlerendersystem)
battlerendersystem.active = False

startrendersystem = StartRenderSystem()
world.add_system(startrendersystem)


###Gamesystems
world.add_system(BlockingSystem())
tos = world.add_system(TurnOrderSystem())
#TODO hackhackhack
tos.battlerendersystem = battlerendersystem
tos.startrendersystem = startrendersystem
###Gamesystems end

worldstepsystem = WorldStepSystem(world,[
    maptographicsystem,
    startrendersystem,
    battlerendersystem,
    tos])
world.add_system(worldstepsystem)

factory.world = world

player_char = factory.create_player_creature(
    name    = "Player",
    texture = "human_m",
    pos     = (2,2),
    mhp     = 10,
    dmg     = 2)

player2 = factory.create_player_creature(
    name    = "Player 2",
    texture = "human_m",
    pos     = (2,10),
    mhp     = 10,
    dmg     = 2)

enemy = factory.create_ai_creature(
    name          = "giant_newt",
    texture       = "newt",
    pos           = (15,10),
    mhp           = 5,
    dmg           = 1,
    corpsetexture = "blood0")

map_w,map_h = 20,15
wall_chance = 42
map_manager.current_map = TileMap(map_w,map_h,wall_chance)

#place the actors TODO make this a function
pos_list = [x for x in map_manager.current_map.wall_map]
pos_list.sort(key=(lambda pos: pos[0] * map_w + pos[1]))
pcs = [player_char,player2]
enemies = [enemy]
for pos in pos_list:
    if len(pcs) == 0:
        break
    if movement.is_pos_free(world,pos):
        e = pcs.pop()
        mp = e.get(MapPos)
        mp.x,mp.y = pos
pos_list.reverse()
for pos in pos_list:
    if len(enemies) == 0:
        break
    if movement.is_pos_free(world,pos):
        e = enemies.pop()
        mp = e.get(MapPos)
        mp.x,mp.y = pos

def regen_map():
    map_manager.current_map = TileMap(map_w,map_h,wall_chance)
def map_left():
    map_manager.current_map.root_pos.x -= 1
def map_right():
    map_manager.current_map.root_pos.x += 1
def map_up():
    map_manager.current_map.root_pos.y -= 1
def map_down():
    map_manager.current_map.root_pos.y += 1
def end_world():
    world.end()
def go_interpreter():
    e = player_char
    import IPython; IPython.embed()
def switch_buffer():
    battlerendersystem.active = not battlerendersystem.active
    startrendersystem.active  = not startrendersystem.active

from input_manager import BattleMode,StartMode
def start_game():
    startrendersystem.active  = False
    battlerendersystem.active = True
    input_manager.activate_mode(BattleMode)


input_manager.quit_handler = end_world
                                                      
input_manager.add_handler(BattleMode,map_right,SDLK_l,KMOD_SHIFT)
input_manager.add_handler(BattleMode,map_left ,SDLK_h,KMOD_SHIFT)
input_manager.add_handler(BattleMode,map_up   ,SDLK_k,KMOD_SHIFT)
input_manager.add_handler(BattleMode,map_down ,SDLK_j,KMOD_SHIFT)
input_manager.add_handler(BattleMode,end_world,SDLK_q)
input_manager.add_handler(BattleMode,switch_buffer,SDLK_t)
input_manager.add_handler(BattleMode,go_interpreter,SDLK_y)
input_manager.add_handler(BattleMode,regen_map,SDLK_F1)

input_manager.add_handler(StartMode,start_game,SDLK_a)
input_manager.add_handler(StartMode,end_world,SDLK_b)
input_manager.activate_mode(StartMode)

def main():
    battle_log.add_msg("Welcome to AoEM.")
    while world.alive:
        world.invoke_system(WorldStepSystem)
    
    world.destroy()

if __name__ == "__main__":
    main()

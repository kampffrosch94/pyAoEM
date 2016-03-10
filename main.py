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

startrendersystem = StartRenderSystem()
startrendersystem.active = False
world.add_system(startrendersystem)

def switch_buffer():
    battlerendersystem.active = not battlerendersystem.active
    startrendersystem.active  = not startrendersystem.active

###Gamesystems
world.add_system(BlockingSystem())
world.add_system(AttackableSystem())
tos = world.add_system(TurnOrderSystem())
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
    pos     = (1,1),
    mhp     = 10,
    dmg     = 2)

player2 = factory.create_player_creature(
    name    = "Player 2",
    texture = "human_m",
    pos     = (2,1),
    mhp     = 10,
    dmg     = 2)

enemy = factory.create_ai_creature(
    name          = "giant_newt",
    texture       = "newt",
    pos           = (5,5),
    mhp           = 5,
    dmg           = 1,
    corpsetexture = "blood0")

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

def go_interpreter():
    e = player_char
    import IPython; IPython.embed()

def switch_player1():
    pc_control.player_char = player_char

def switch_player2():
    pc_control.player_char = player2

from input_manager import BattleMode
input_manager.quit_handler = end_world
                                                      
input_manager.add_handler(BattleMode,map_right,SDLK_l,KMOD_SHIFT)
input_manager.add_handler(BattleMode,map_left ,SDLK_h,KMOD_SHIFT)
input_manager.add_handler(BattleMode,map_up   ,SDLK_k,KMOD_SHIFT)
input_manager.add_handler(BattleMode,map_down ,SDLK_j,KMOD_SHIFT)
input_manager.add_handler(BattleMode,end_world,SDLK_q)
input_manager.add_handler(BattleMode,delete_test,SDLK_x)
input_manager.add_handler(BattleMode,switch_buffer,SDLK_t)
input_manager.add_handler(BattleMode,go_interpreter,SDLK_y)
input_manager.add_handler(BattleMode,switch_player1,SDLK_F1)
input_manager.add_handler(BattleMode,switch_player2,SDLK_F2)
input_manager.activate_mode(BattleMode)

def main():
    battle_log.add_msg("Welcome to AoEM.")
    while world.alive:
        world.invoke_system(WorldStepSystem)
    
    world.destroy()

if __name__ == "__main__":
    main()

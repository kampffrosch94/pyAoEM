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

player_char = Entity(world)
player_char.name = "Player Character"

texture = sdl_manager.load_texture("human_m")
gc = Graphic(texture,z=1)
mc = MapPos(1,1)
player_char.set(gc)
player_char.set(BattleBuffer())
player_char.set(mc)



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


battle_log.add_msg("Message 1")
battle_log.add_msg("Message 2")
counter = 3
def add_msg():
    global counter
    msg = "Message " + str(counter) 
    battle_log.add_msg(msg)
    counter += 1

def move_right():
    player_char.get(MapPos).x += 1
def move_left():
    player_char.get(MapPos).x -= 1
def move_up():
    player_char.get(MapPos).y -= 1
def move_down():
    player_char.get(MapPos).y += 1

def go_interpreter():
    global world
    import IPython; IPython.embed()

from input_manager import BattleMode
input_manager.add_handler(BattleMode,SDLK_l,move_right)
input_manager.add_handler(BattleMode,SDLK_h,move_left)
input_manager.add_handler(BattleMode,SDLK_k,move_up)
input_manager.add_handler(BattleMode,SDLK_j,move_down)

input_manager.add_handler(BattleMode,SDLK_d,map_right)
input_manager.add_handler(BattleMode,SDLK_a,map_left)
input_manager.add_handler(BattleMode,SDLK_w,map_up)
input_manager.add_handler(BattleMode,SDLK_s,map_down)
input_manager.add_handler(BattleMode,SDLK_q,end_world)
input_manager.quit_handler = end_world
input_manager.add_handler(BattleMode,SDLK_m,add_msg)
input_manager.add_handler(BattleMode,SDLK_x,delete_test)
input_manager.add_handler(BattleMode,SDLK_t,switch_buffer)
input_manager.add_handler(BattleMode,SDLK_y,go_interpreter)
input_manager.activate_mode(BattleMode)


def main():
    while world.alive:
        world.invoke_system(WorldStepSystem)
    
    world.destroy()

if __name__ == "__main__":
    main()

import random
import sdl2
import sdl_manager
import map_manager
import input_manager
import ecs
import systems
import game_systems
import components
import factory
import movement
import pc_control
import battle_log

world = ecs.World()

maptographicsystem = systems.MapToGraphicSystem()
world.add_system(maptographicsystem)

battlerendersystem = systems.BattleRenderSystem()
world.add_system(battlerendersystem)
battlerendersystem.active = False

startrendersystem = systems.StartRenderSystem()
world.add_system(startrendersystem)


###Gamesystems
world.add_system(game_systems.BlockingSystem())
tos = world.add_system(game_systems.TurnOrderSystem())
#TODO hackhackhack
tos.battlerendersystem = battlerendersystem
tos.startrendersystem = startrendersystem
###Gamesystems end

worldstepsystem = systems.WorldStepSystem(world,[
    maptographicsystem,
    startrendersystem,
    battlerendersystem,
    tos])
world.add_system(worldstepsystem)

factory.world = world

player_number = random.randint(1,3)
enemy_number = random.randint(3,10)
pcs = []
enemies = []
for i in range(player_number):
    player_char = factory.create_player_creature(
        name    = "Player "+str(i+1),
        texture = "human_m",
        pos     = (2,2),
        mhp     = 10,
        dmg     = 2)
    pcs.append(player_char)

for i in range(enemy_number):
    enemy = factory.create_ai_creature(
        name          = "giant newt "+str(i+1),
        texture       = "newt",
        pos           = (15,10),
        mhp           = 5,
        dmg           = 1,
        corpsetexture = "blood0")
    enemies.append(enemy)

map_w,map_h = 20,15
wall_chance = 42
map_manager.current_map = map_manager.TileMap(map_w,map_h,wall_chance)

#place the actors TODO make this a function
pos_list = [x for x in map_manager.current_map.wall_map]
pos_list.sort(key=(lambda pos: pos[0] * map_w + pos[1]))
for pos in pos_list:
    if len(pcs) == 0:
        break
    if movement.is_pos_free(world,pos):
        e = pcs.pop()
        mp = e.get(components.MapPos)
        mp.x,mp.y = pos
pos_list.reverse()
for pos in pos_list:
    if len(enemies) == 0:
        break
    if movement.is_pos_free(world,pos):
        e = enemies.pop()
        mp = e.get(components.MapPos)
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

from input_manager import BattleMode,StartMode
def start_game():
    startrendersystem.active  = False
    battlerendersystem.active = True
    input_manager.activate_mode(BattleMode)


input_manager.quit_handler = end_world
                                                      
input_manager.add_handler(BattleMode,map_right,sdl2.SDLK_l,sdl2.KMOD_SHIFT)
input_manager.add_handler(BattleMode,map_left ,sdl2.SDLK_h,sdl2.KMOD_SHIFT)
input_manager.add_handler(BattleMode,map_up   ,sdl2.SDLK_k,sdl2.KMOD_SHIFT)
input_manager.add_handler(BattleMode,map_down ,sdl2.SDLK_j,sdl2.KMOD_SHIFT)
input_manager.add_handler(BattleMode,end_world,sdl2.SDLK_q)
input_manager.add_handler(BattleMode,go_interpreter,sdl2.SDLK_y)
input_manager.add_handler(BattleMode,regen_map,sdl2.SDLK_F1)

input_manager.add_handler(StartMode,start_game,sdl2.SDLK_a)
input_manager.add_handler(StartMode,end_world,sdl2.SDLK_b)
input_manager.activate_mode(StartMode)

def main():
    battle_log.add_msg("Welcome to AoEM.")
    while world.alive:
        world.invoke_system(systems.WorldStepSystem)
    
    world.destroy()

if __name__ == "__main__":
    main()

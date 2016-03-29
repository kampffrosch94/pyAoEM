import random
import sdl2
import map_
import input_
import ecs
import game
import factory
import movement
import battle_log
import battle
import start

world = ecs.World()

battlerendersystem = battle.BattleRenderSystem()
world.add_system(battlerendersystem)
battlerendersystem.active = False

startrendersystem = start.StartRenderSystem()
world.add_system(startrendersystem)

###Gamesystems
world.add_system(game.BlockingSystem())
tos = world.add_system(game.TurnOrderSystem())
#TODO hackhackhack
tos.battlerendersystem = battlerendersystem
tos.startrendersystem = startrendersystem
###Gamesystems end

worldstepsystem = ecs.WorldStepSystem(world,[
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
map_.current_map = map_.TileMap(map_w,map_h,wall_chance)

#place the actors TODO make this a function
pos_list = [x for x in map_.current_map.wall_map]
pos_list.sort(key=(lambda pos: pos[0] * map_w + pos[1]))
for pos in pos_list:
    if len(pcs) == 0:
        break
    if movement.is_pos_free(world,pos):
        e = pcs.pop()
        mp = e.get(game.MapPos)
        mp.x,mp.y = pos
pos_list.reverse()
for pos in pos_list:
    if len(enemies) == 0:
        break
    if movement.is_pos_free(world,pos):
        e = enemies.pop()
        mp = e.get(game.MapPos)
        mp.x,mp.y = pos

def regen_map():
    map_.current_map = TileMap(map_w,map_h,wall_chance)
def map_left():
    map_.current_map.root_pos.x -= 1
def map_right():
    map_.current_map.root_pos.x += 1
def map_up():
    map_.current_map.root_pos.y -= 1
def map_down():
    map_.current_map.root_pos.y += 1
def end_world():
    world.end()
def go_interpreter():
    e = player_char
    import IPython; IPython.embed()

from input_ import BattleMode,StartMode
def start_game():
    startrendersystem.active  = False
    battlerendersystem.active = True
    input_.activate_mode(BattleMode)


input_.quit_handler = end_world
                                                      
input_.add_handler(BattleMode,map_right,sdl2.SDLK_l,sdl2.KMOD_SHIFT)
input_.add_handler(BattleMode,map_left ,sdl2.SDLK_h,sdl2.KMOD_SHIFT)
input_.add_handler(BattleMode,map_up   ,sdl2.SDLK_k,sdl2.KMOD_SHIFT)
input_.add_handler(BattleMode,map_down ,sdl2.SDLK_j,sdl2.KMOD_SHIFT)
input_.add_handler(BattleMode,end_world,sdl2.SDLK_q)
input_.add_handler(BattleMode,go_interpreter,sdl2.SDLK_y)
input_.add_handler(BattleMode,regen_map,sdl2.SDLK_F1)

input_.add_handler(StartMode,start_game,sdl2.SDLK_a)
input_.add_handler(StartMode,end_world,sdl2.SDLK_b)
input_.activate_mode(StartMode)

def main():
    battle_log.add_msg("Welcome to AoEM.")
    while world.alive:
        world.invoke_system(ecs.WorldStepSystem)
    
    world.destroy()

if __name__ == "__main__":
    main()

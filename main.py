from sdl2 import *
from sdl2.sdlimage import *
from ecs import World,Entity 
from systems import *
from components import *
from errors import SDL_Exception
from utility import Position
import sdl_manager

def main():
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

    tilemapsystem = TileMapSystem(world)
    world.add_system(tilemapsystem)

    logsystem = LogSystem(world)
    logsystem.add_msg("Message 1")
    logsystem.add_msg("Message 2")
    world.add_system(logsystem)

    inputsystem = InputSystem(world)
    world.add_system(inputsystem)
    worldstepsystem = WorldStepSystem(world,[
        maptographicsystem,
        tilemapsystem,
        logsystem,
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

    player_char.set(InputMap())

    def move_right():
        player_char.get(MapPos).x += 1
    def move_left():
        player_char.get(MapPos).x -= 1
    def move_up():
        player_char.get(MapPos).y -= 1
    def move_down():
        player_char.get(MapPos).y += 1

    player_char.get(InputMap).add_key_handler(SDLK_l,move_right)
    player_char.get(InputMap).add_key_handler(SDLK_h,move_left)
    player_char.get(InputMap).add_key_handler(SDLK_k,move_up)
    player_char.get(InputMap).add_key_handler(SDLK_j,move_down)
    
    battlefield = Entity(world)
    texturepath = "cobble_blood1"
    default_texture = sdl_manager.load_texture(texturepath)
    tmap = TileMap(1000,1000,default_texture)

    map_texture = SDL_CreateTexture(
            sdl_manager.renderer,
            SDL_PIXELFORMAT_RGBA8888,
            SDL_TEXTUREACCESS_TARGET,640,480)
    map_graphic = Graphic(map_texture,0,0,640,480,z=0)
    battlefield.set(map_graphic)
    battlefield.set(BattleBuffer())
    battlefield.set(tmap)

    def map_left():
        maptographicsystem.root_pos.x -= 1
        tmap.root_pos.x -= 1
    def map_right():
        maptographicsystem.root_pos.x += 1
        tmap.root_pos.x += 1
    def map_up():
        maptographicsystem.root_pos.y -= 1
        tmap.root_pos.y -= 1
    def map_down():
        maptographicsystem.root_pos.y += 1
        tmap.root_pos.y += 1
    def end_world():
        world.end()
    def delete_test():
        player_char.delete(Graphic)

    counter = 3
    def add_msg():
        nonlocal counter
        msg = "Message " + str(counter) 
        logsystem.add_msg(msg)
        counter += 1

    global_input = Entity(world)
    global_input.set(InputMap())
    global_input.get(InputMap).add_key_handler(SDLK_d,map_right)
    global_input.get(InputMap).add_key_handler(SDLK_a,map_left)
    global_input.get(InputMap).add_key_handler(SDLK_w,map_up)
    global_input.get(InputMap).add_key_handler(SDLK_s,map_down)
    global_input.get(InputMap).add_key_handler(SDLK_q,end_world)
    global_input.get(InputMap).add_key_handler(SDLK_m,add_msg)
    global_input.get(InputMap).add_key_handler(SDLK_x,delete_test)
    global_input.get(InputMap).add_key_handler(SDLK_t,switch_buffer)


    while world.alive:
        world.invoke_system(WorldStepSystem)
    
    world.destroy()

if __name__ == "__main__":
    main()

from sdl2 import *
from sdl2.sdlimage import *
from ecs import World,Entity 
from systems import *
from components import *
from errors import SDL_Exception
from utility import Position
def main():
    world = World()

    mapsystem = MapSystem(world)
    world.add_system(mapsystem)

    maptographicsystem = MapToGraphicSystem(world)
    world.add_system(maptographicsystem)

    rendersystem = RenderSystem(world)
    world.add_system(rendersystem)

    tilemapsystem = TileMapSystem(rendersystem.renderer)
    world.add_system(tilemapsystem)

    inputsystem = InputSystem(world)
    world.add_system(inputsystem)
    worldstepsystem = WorldStepSystem(world,[
        mapsystem,
        maptographicsystem,
        tilemapsystem,
        rendersystem,
        inputsystem])
    world.add_system(worldstepsystem)

    player_char = Entity(world)
    player_char.name = "Player Character"
    
    texturepath = ("gfx/human_m.png")
    gc = rendersystem.load_graphic(texturepath,z=1)
    mc = MapPos(1,1)
    player_char.set(gc)
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
    texturepath = ("gfx/cobble_blood1.png")
    default_texture = rendersystem.load_graphic(texturepath).texture
    tmap = TileMap(1000,1000,default_texture)
    map_texture = SDL_CreateTexture(
            rendersystem.renderer,
            SDL_PIXELFORMAT_RGBA8888,
            SDL_TEXTUREACCESS_TARGET,640,480)
    map_graphic = Graphic(map_texture,0,0,640,480,z=0)
    battlefield.set(map_graphic)
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

    global_input = Entity(world)
    global_input.set(InputMap())
    global_input.get(InputMap).add_key_handler(SDLK_d,map_right)
    global_input.get(InputMap).add_key_handler(SDLK_a,map_left)
    global_input.get(InputMap).add_key_handler(SDLK_w,map_up)
    global_input.get(InputMap).add_key_handler(SDLK_s,map_down)
    global_input.get(InputMap).add_key_handler(SDLK_q,end_world)

    while world.alive:
        world.invoke_system(WorldStepSystem)
    
    world.destroy()

if __name__ == "__main__":
    main()

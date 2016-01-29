from sdl2 import *
from sdl2.sdlimage import *
from ecs import World,Entity 
from systems import *
from components import *
from errors import SDL_Exception
from utility import Position
def main():
    world = World()

    mtgs = MapToGraphicSystem(world)
    world.add_system(mtgs)

    rendersystem = RenderSystem(world)
    world.add_system(rendersystem)

    inputsystem = InputSystem(world)
    world.add_system(inputsystem)
    worldstepsystem = WorldStepSystem(world,
            [mtgs,rendersystem,inputsystem])
    world.add_system(worldstepsystem)

    player_char = Entity(world)
    
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

    for x in range(20):
        for y in range(20):
            tile = Entity(world)
            texturepath = ("gfx/cobble_blood1.png")
            gc = rendersystem.load_graphic(texturepath)
            tile.set(gc)
            tile.set(MapPos(x,y))

    while world.alive:
        world.invoke_system(WorldStepSystem)
    
    world.destroy()

if __name__ == "__main__":
    main()

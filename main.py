from sdl2 import *
from sdl2.sdlimage import *
from ecs import World,Entity 
from systems import *
from components import *
from errors import SDL_Exception


def main():

    world = World()

    rendersystem = RenderSystem(world)
    world.add_system(rendersystem)

    inputsystem = InputSystem(world)
    world.add_system(inputsystem)
    worldstepsystem = WorldStepSystem(world,[rendersystem,inputsystem])
    world.add_system(worldstepsystem)

    player_char = Entity(world)
    
    texture = rendersystem.load_texture("gfx/human_m.png")
    player_char.set(MapComponent(texture,32,32,32,32,1))

    player_char.set(InputComponent())

    def move_right():
        player_char.get(MapComponent).x += 32
    def move_left():
        player_char.get(MapComponent).x -= 32
    def move_up():
        player_char.get(MapComponent).y -= 32
    def move_down():
        player_char.get(MapComponent).y += 32

    player_char.get(InputComponent).add_key_handler(SDLK_l,move_right)
    player_char.get(InputComponent).add_key_handler(SDLK_h,move_left)
    player_char.get(InputComponent).add_key_handler(SDLK_k,move_up)
    player_char.get(InputComponent).add_key_handler(SDLK_j,move_down)

    texture = rendersystem.load_texture("gfx/snake0.png")
    for x in range(20):
        for y in range(20):
            tile = Entity(world)
            tile.set(MapComponent(texture,32*x,32*y,32,32))

    while world.alive:
        world.invoke_system(worldstepsystem)
    
    world.destroy()

if __name__ == "__main__":
    main()

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

    e = Entity(world)
    
    texture = rendersystem.load_texture("gfx/human_m.png")
    e.graphiccomponent = GraphicComponent(texture,32,32)

    e.inputcomponent = InputComponent()

    def move_right():
        e.graphiccomponent.x += 16
    def move_left():
        e.graphiccomponent.x -= 16
    def move_up():
        e.graphiccomponent.y -= 16
    def move_down():
        e.graphiccomponent.y += 16

    e.inputcomponent.add_key_handler(SDLK_l,move_right)
    e.inputcomponent.add_key_handler(SDLK_h,move_left)
    e.inputcomponent.add_key_handler(SDLK_k,move_up)
    e.inputcomponent.add_key_handler(SDLK_j,move_down)

    while world.alive:
        world.invoke_system(worldstepsystem)
    
    world.destroy()

if __name__ == "__main__":
    main()

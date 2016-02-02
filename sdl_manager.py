from sdl2 import *
from sdl2.sdlimage import *

img_paths = {
        "human_m" : b"gfx/human_m.png",
        "cobble_blood1" : b"gfx/cobble_blood1.png"
}

loaded_textures = {}

def load_texture(renderer, texture_name):
    global img_paths,loaded_textures
    if texture_name in loaded_textures:
        return loaded_textures[texture_name]
    surface = IMG_Load(img_paths[texture_name])
    if surface == None:
        raise OSError("File "+path+" could not be loaded.")
    texture = SDL_CreateTextureFromSurface(renderer,surface) 
    if texture == None:
        raise SDL_Exception

    SDL_FreeSurface(surface)

    loaded_textures[texture_name] = texture
    return texture

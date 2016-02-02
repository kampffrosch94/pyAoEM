from sdl2 import *
from sdl2.sdlimage import *
import atexit


SDL_Init(SDL_INIT_VIDEO)
IMG_Init(IMG_INIT_JPG)
window = SDL_CreateWindow(b"AoEM",0,0,640,640,SDL_SWSURFACE);
renderer = SDL_CreateRenderer(window,-1,SDL_RENDERER_ACCELERATED)
if renderer == None:
    raise SDL_Exception()

img_paths = {
        "human_m"       : b"gfx/human_m.png",
        "cobble_blood1" : b"gfx/cobble_blood1.png"
}

loaded_textures = {}

def load_texture(texture_name):
    global renderer,img_paths,loaded_textures
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

@atexit.register
def unload():
    global loaded_textures
    for texture in loaded_textures.values():
        SDL_DestroyTexture(texture)
    global renderer,window
    SDL_DestroyRenderer(renderer)
    SDL_DestroyWindow(window)
    IMG_Quit()
    SDL_Quit()

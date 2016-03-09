from sdl2 import *
from sdl2.sdlimage import *
from sdl2.sdlttf import *
from components import Graphic
import atexit


SDL_Init(SDL_INIT_VIDEO)
IMG_Init(IMG_INIT_JPG)
TTF_Init()
WINDOW_W = 640
WINDOW_H = 640
FONT_SIZE = 14
window = SDL_CreateWindow(b"AoEM",0,0,WINDOW_W,WINDOW_H,SDL_SWSURFACE);
renderer = SDL_CreateRenderer(window,-1,SDL_RENDERER_ACCELERATED)
if renderer == None:
    raise SDL_Exception()
#font = TTF_OpenFont(b"fonts/OpenSans-Regular.ttf",20)
#font = TTF_OpenFont(b"fonts/AnonymousPro-Regular.ttf",20)
font = TTF_OpenFont(b"fonts/VeraMono.ttf",FONT_SIZE)
default_fg = SDL_Color()

img_paths = {
        "human_m"       : b"gfx/human_m.png",
        "cobble_blood1" : b"gfx/cobble_blood1.png",
        "newt"          : b"gfx/giant_newt.png",
        "blood0"        : b"gfx/blood_red00.png"
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

def create_text_texture(text,fg = None):
    global renderer,font,default_fg
    if fg is None:
        fg = default_fg
    if hasattr(text,"encode"):
        text = text.encode()
    #text_surface = TTF_RenderText_Solid(font,text,fg)
    text_surface = TTF_RenderText_Blended_Wrapped(font,text,fg,WINDOW_W)
    text_texture = SDL_CreateTextureFromSurface(renderer,text_surface)
    SDL_FreeSurface(text_surface)
    return text_texture

def create_text_graphic(text,fg = None):
    return Graphic(create_text_texture(text,fg))

@atexit.register
def unload():
    global loaded_textures
    for texture in loaded_textures.values():
        SDL_DestroyTexture(texture)
    global renderer,window
    SDL_DestroyRenderer(renderer)
    SDL_DestroyWindow(window)
    IMG_Quit()
    TTF_Quit()
    SDL_Quit()

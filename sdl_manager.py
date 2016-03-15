import sdl2
import sdl2.sdlimage as sdlimage
import sdl2.sdlttf as sdlttf
import errors
import components
import atexit

WINDOW_W = 640
WINDOW_H = 640
FONT_SIZE = 14

sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)
sdlimage.IMG_Init(sdlimage.IMG_INIT_JPG)
sdlttf.TTF_Init()

window = sdl2.SDL_CreateWindow(b"AoEM",0,0,WINDOW_W,WINDOW_H,
        sdl2.SDL_SWSURFACE)

renderer = sdl2.SDL_CreateRenderer(window,-1,sdl2.SDL_RENDERER_ACCELERATED)
if renderer == None:
    raise errors.SDL_Exception()

font = sdlttf.TTF_OpenFont(b"fonts/VeraMono.ttf",FONT_SIZE)
default_fg = sdl2.SDL_Color()

img_paths = {
        "human_m"       : b"gfx/human_m.png",
        "cobble_blood1" : b"gfx/cobble_blood1.png",
        "newt"          : b"gfx/giant_newt.png",
        "blood0"        : b"gfx/blood_red00.png",
        "lair0"         : b"gfx/walls/lair0.png"
}

loaded_textures = {}

def load_texture(texture_name):
    if texture_name in loaded_textures:
        return loaded_textures[texture_name]
    surface = sdlimage.IMG_Load(img_paths[texture_name])
    if surface == None:
        raise OSError("File "+texture_name+" could not be loaded.")
    texture = sdl2.SDL_CreateTextureFromSurface(renderer,surface) 
    if texture == None:
        raise SDL_Exception

    sdl2.SDL_FreeSurface(surface)

    loaded_textures[texture_name] = texture
    return texture

def create_text_texture(text,fg = None):
    if fg is None:
        fg = default_fg
    if hasattr(text,"encode"):
        text = text.encode()
    text_surface = sdlttf.TTF_RenderText_Blended_Wrapped(
            font,text,fg,WINDOW_W)
    text_texture = sdl2.SDL_CreateTextureFromSurface(renderer,text_surface)
    sdl2.SDL_FreeSurface(text_surface)
    return text_texture

def create_text_graphic(text,fg = None):
    return components.Graphic(create_text_texture(text,fg))

@atexit.register
def unload():
    for texture in loaded_textures.values():
        sdl2.SDL_DestroyTexture(texture)
    sdl2.SDL_DestroyRenderer(renderer)
    sdl2.SDL_DestroyWindow(window)
    sdlimage.IMG_Quit()
    sdlttf.TTF_Quit()
    sdl2.SDL_Quit()

import sdl2
import sdl2.sdlimage as sdlimage
import sdl2.sdlttf as sdlttf
import atexit

WINDOW_W = 640
WINDOW_H = 640
FONT_SIZE = 14

sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)
sdlimage.IMG_Init(sdlimage.IMG_INIT_PNG)
sdlttf.TTF_Init()

window = sdl2.SDL_CreateWindow(b"AoEM",0,0,WINDOW_W,WINDOW_H,
                               sdl2.SDL_SWSURFACE)

renderer = sdl2.SDL_CreateRenderer(window,-1,sdl2.SDL_RENDERER_ACCELERATED)
if renderer == None:
    raise SDL_Exception()

font = sdlttf.TTF_OpenFont(b"fonts/VeraMono.ttf",FONT_SIZE)
default_fg = sdl2.SDL_Color()

img_paths = {
    "human_m"       : b"gfx/human_m.png",
    "cobble_blood1" : b"gfx/cobble_blood1.png",
    "newt"          : b"gfx/giant_newt.png",
    "blood0"        : b"gfx/blood_red00.png",
    "lair0"         : b"gfx/walls/lair0.png",
    "cursor_green"  : b"gfx/cursor_green.png"
}

loaded_textures = {}

def reset_render_target():
    sdl2.SDL_SetRenderTarget(renderer, None)

def render_clear():
    sdl2.SDL_RenderClear(renderer)

def render_present():
    sdl2.SDL_RenderPresent(renderer)

class Graphic(object):
    """Contains a texture and the position where it should be rendered.

    Change x and y to change the position where the graphic will be
    rendered from the RenderSystem.
    """
    def __init__(self,texture,x,y,w,h,z=1,destroy=False):
        self.texture = texture
        if z < 0 or z > 1:
            raise NotImplementedError()
        self.z = z
        self.w = w
        self.h = h
        self.src_rect = sdl2.SDL_Rect(0,0,w,h)
        self.dest_rect = sdl2.SDL_Rect(x,y,w,h)

        if destroy:
            def destroy_f():
                sdl2.SDL_DestroyTexture(self.texture)
            self.destroy = destroy_f

    @property
    def x(self):
        return self.dest_rect.x
    @x.setter
    def x(self,value):
        self.dest_rect.x = value

    @property
    def y(self):
        return self.dest_rect.y
    @y.setter
    def y(self,value):
        self.dest_rect.y = value

    def render(self):
        sdl2.SDL_RenderCopy(renderer,
                            self.texture,
                            self.src_rect,
                            self.dest_rect)

    def make_render_target(self):
        sdl2.SDL_SetRenderTarget(renderer, self.texture)

    def corpsify(self): #placeholder
        self.texture = load_graphic("blood0").texture
        self.z = 0

def load_graphic(texture_name):
    if texture_name in loaded_textures:
        cached = loaded_textures[texture_name]
        return Graphic(*cached)
    surface = sdlimage.IMG_Load(img_paths[texture_name])
    if surface == None:
        raise OSError("File "+texture_name+" could not be loaded.")
    texture = sdl2.SDL_CreateTextureFromSurface(renderer,surface)
    if texture == None:
        raise SDL_Exception()

    rect = surface.contents.clip_rect
    g = Graphic(texture,rect.x,rect.y,rect.w,rect.h)
    sdl2.SDL_FreeSurface(surface)
    loaded_textures[texture_name] = (texture,g.x,g.y,g.w,g.h)
    return g

def create_graphic(x,y,w,h,z=1):
    texture = sdl2.SDL_CreateTexture(
        renderer,
        sdl2.SDL_PIXELFORMAT_RGBA8888,
        sdl2.SDL_TEXTUREACCESS_TARGET, w, h)
    return Graphic(texture, x, y, w, h, z, destroy=True)

def create_text_graphic(text,x=0,y=0,fg = None,max_width = WINDOW_W):
    if fg is None:
        fg = default_fg
    if hasattr(text,"encode"):
        text = text.encode()
    text_surface = sdlttf.TTF_RenderText_Blended_Wrapped(
        font,text,fg,max_width)
    text_texture = sdl2.SDL_CreateTextureFromSurface(renderer,text_surface)

    rect = text_surface.contents.clip_rect
    g = Graphic(text_texture,x,y,rect.w,rect.h,destroy=True)
    sdl2.SDL_FreeSurface(text_surface)
    return g

class SDL_Exception(Exception):
    def __init__(self):
        Exception.__init__()
        self.value = sdl2.SDL_GetError()
    def __str__(self):
        return repr(self.value)

@atexit.register
def unload():
    for texture in loaded_textures.values():
        sdl2.SDL_DestroyTexture(texture[0])
    sdl2.SDL_DestroyRenderer(renderer)
    sdl2.SDL_DestroyWindow(window)
    sdlimage.IMG_Quit()
    sdlttf.TTF_Quit()
    sdl2.SDL_Quit()

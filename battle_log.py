"""Holds and Renders the Messagelog in battles."""
import sdl2
import res

messages = []

log_src = sdl2.SDL_Rect(w=640, h=160)
log_dest = sdl2.SDL_Rect(x=0, y=480, w=log_src.w, h=log_src.h)

texture = sdl2.SDL_CreateTexture(
    res.renderer,
    sdl2.SDL_PIXELFORMAT_RGBA8888,
    sdl2.SDL_TEXTUREACCESS_TARGET,log_src.w,log_src.h)

dirty = False

def add_msg(msg):
    global dirty
    messages.append(msg)
    if len(messages) > 9:
        del messages[0]
    dirty = True

def update():
    global dirty
    if dirty:
        sdl2.SDL_SetRenderTarget(res.renderer,texture)
        sdl2.SDL_RenderClear(res.renderer)
        y = 0
        for msg in messages:
            g = res.create_text_graphic(msg)
            g.y = y
            sdl2.SDL_RenderCopy(
                res.renderer,
                g.texture,
                g.src_rect,
                g.dest_rect)
            y += g.h
            sdl2.SDL_DestroyTexture(g.texture)
        sdl2.SDL_SetRenderTarget(res.renderer,None)
        dirty = False

def render():
    update()
    sdl2.SDL_RenderCopy(res.renderer,texture,log_src,log_dest)

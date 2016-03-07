"""Holds and Renders the Messagelog in battles."""
from sdl_manager import renderer
from components import Graphic
from sdl2 import *
import sdl_manager

messages = []
dirty = False

log_src = SDL_Rect(w=640,h=160)
log_dest = SDL_Rect(x=0,y=480,w=log_src.w,h=log_src.h)

texture = SDL_CreateTexture(renderer,
        SDL_PIXELFORMAT_RGBA8888,
        SDL_TEXTUREACCESS_TARGET,log_src.w,log_src.h)

def add_msg(msg):
    global dirty
    messages.append(msg)
    if len(messages) > 9:
        del messages[0]
    dirty = True

def update():
    global dirty
    if dirty:
        SDL_SetRenderTarget(renderer,texture)
        SDL_RenderClear(renderer)
        y = 0
        for msg in messages:
            g = sdl_manager.create_text_graphic(msg)
            g.y = y
            SDL_RenderCopy( renderer,
                            g.texture,
                            g.src_rect,
                            g.dest_rect)
            y += g.h
            g.destroy()
        SDL_SetRenderTarget(renderer,None)
        dirty = False

def render():
    update()
    SDL_RenderCopy(renderer,texture,log_src,log_dest)

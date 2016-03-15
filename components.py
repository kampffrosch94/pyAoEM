"""This File holds the various components of the ecs.

A component should only hold data and no functionality if possible."""

import sdl2
import ctypes
import utility
import errors

class MapPos(utility.Position):
    """The position of an entity on the map."""

class Buffer(object):
    """All Buffer components should inherit from this one."""
    pass

class BattleBuffer(Buffer):
    pass

class StartBuffer(Buffer):
    pass

class Graphic(object):
    """Contains a texture and the position where it should be rendered.

    Change x and y to change the position where the graphic will be
    rendered from the RenderSystem.
    """
    def __init__(self,texture,x=0,y=0,w=0,h=0,z=1):
        self.texture = texture
        if z < 0 or z > 1:
            raise NotImplementedError()
        self.z = z
        self.x = x
        self.y = y
        if w == 0 or h == 0:
            flags = sdl2.Uint32()
            access = sdl2.c_int()
            w = sdl2.c_int()
            h = sdl2.c_int()
            ret = sdl2.SDL_QueryTexture(texture,
                                        ctypes.byref(flags),
                                        ctypes.byref(access),
                                        ctypes.byref(w),
                                        ctypes.byref(h))
            if ret == -1:
                raise errors.SDL_Exception()
            w = w.value
            h = h.value

        self.w = w
        self.h = h
        self.src_rect = sdl2.SDL_Rect(0,0,w,h)
        self._dest_rect = sdl2.SDL_Rect(x,y,w,h)
        self.active = True

    @property
    def dest_rect(self):
        self._dest_rect.x = self.x
        self._dest_rect.y = self.y
        return self._dest_rect

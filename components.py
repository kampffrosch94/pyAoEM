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


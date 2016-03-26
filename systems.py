import sdl2
import ecs
import components
import utility
import res
import map_manager
import battle_log

class WorldStepSystem(ecs.System):
    """The System which runs the gameloop"""
    def __init__(self,world,systems):
        ecs.System.__init__(self)
        self.systems = [s.__class__ for s in systems]
        self.world = world

    def process(self,entities):
        for s in self.systems:
            self.world.invoke_system(s)

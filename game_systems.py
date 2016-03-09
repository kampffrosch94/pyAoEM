from ecs import System
from game_components import Blocking
from components import MapPos
from game_components import Health

class BlockingSystem(System):
    """Just for holding blocking entities."""
    def __init__(self):
        System.__init__(self,[MapPos,Blocking])
        self.active = False

class AttackableSystem(System):
    """Just for holding blocking entities."""
    def __init__(self):
        System.__init__(self,[MapPos,Health])
        self.active = False

from ecs import System
from game_components import Blocking, Health, Fatigue
from components import MapPos
from game_events import Act

class BlockingSystem(System):
    """Just for holding blocking entities."""
    def __init__(self):
        System.__init__(self,[MapPos,Blocking])
        self.active = False

class TurnOrderSystem(System):
    def __init__(self):
        System.__init__(self,[Fatigue])

    def process(self, entities):
        actor = min(entities, key=(lambda e: e.get(Fatigue).value))
        print("%s acts." % actor.name)
        actor.handle_event(Act())

from ecs import System
from game_components import Blocking, Health, Fatigue, Team
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
        #TODO rework this
        if all(entities[0].get(Team) == e.get(Team) for e in entities):
            #GAME OVER
            self.game_over(entities[0].get(Team).team_name=="player_team")
        else:
        #end of filth
            actor = min(entities, key=(lambda e: e.get(Fatigue).value))
            print("%s acts." % actor.name)
            actor.handle_event(Act())

    #TODO filth again
    def game_over(self,victory):
        import input_manager
        from input_manager import StartMode
        from sdl2 import SDLK_b
        self.startrendersystem.active  = True
        self.battlerendersystem.active = False
        input_manager.activate_mode(StartMode)
        input_manager.clear_mode(StartMode)
        input_manager.add_handler(StartMode,input_manager.quit_handler,
                SDLK_b)
        if victory:
            self.startrendersystem.set_end_game(
                    "You win a glorious VICTORY!!!")
        else:
            self.startrendersystem.set_end_game(
                    "You were DEFEATED!!!")
        self.startrendersystem.process([]) 
        input_manager.handle_event()

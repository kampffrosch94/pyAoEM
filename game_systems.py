import ecs
import game_components
import components
import game_events

class BlockingSystem(ecs.System):
    """Just for holding blocking entities."""
    def __init__(self):
        ecs.System.__init__(self,[components.MapPos,
                                  game_components.Blocking])
        self.active = False

class TurnOrderSystem(ecs.System):
    def __init__(self):
        ecs.System.__init__(self,[game_components.Fatigue])

    def process(self, entities):
        #TODO rework this
        if all(entities[0].get(game_components.Team)
               == e.get(game_components.Team) for e in entities):
            #GAME OVER
            self.game_over(entities[0].get(game_components.Team)
                           .team_name=="player_team")
        else:
        #end of filth
            actor = min(entities, key=(lambda e: e.get(game_components.
                                                       Fatigue).value))
            print("%s acts." % actor.name)
            actor.handle_event(game_events.Act())

    #TODO filth again
    def game_over(self,victory):
        import input_
        import sdl2
        self.startrendersystem.active  = True
        self.battlerendersystem.active = False
        input_.activate_mode(input_.StartMode)
        input_.clear_mode(input_.StartMode)
        input_.add_handler(input_.StartMode,
                           input_.quit_handler,
                           sdl2.SDLK_b)
        if victory:
            self.startrendersystem.set_end_game(
                "You win a glorious VICTORY!!!")
        else:
            self.startrendersystem.set_end_game(
                "You were DEFEATED!!!")
        self.startrendersystem.process([])
        input_.handle_event()

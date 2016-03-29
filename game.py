import ecs
import res
import battle_log
import utility

###simple components
class Blocking(object):
    """Only one blocking entity can be at a map_pos."""
    pass

class MapPos(utility.Position):
    """The position of an entity on the map."""

class CorpseGraphic(object):
    #should be replaced with corpsify
    def __init__(self,graphic):
        self.texture = graphic.texture

class Team(object):
    def __init__(self,team_name):
        self.team_name = team_name

    def __eq__(self,other):
        return self.team_name == other.team_name
# Events

class TakeDamage(object):
    def __init__(self, dmg_event):
        self.amount = dmg_event.amount
        self.handler_name = "take_damage"

class DealDamage(object):
    def __init__(self, amount=0):
        self.amount = amount
        self.handler_name = "deal_damage"

class Act(object):
    def __init__(self):
        self.handler_name = "act"

class PayFatigue(object):
    def __init__(self, amount):
        self.amount = amount
        self.handler_name = "pay_fatigue"

###Eventhandling components

class Health(object):
    def __init__(self,entity,max_hp):
        self.entity = entity
        self.max_hp = max_hp
        self.hp = max_hp
        self.priority = 0

    def take_damage(self,event : TakeDamage):
        self.hp -= event.amount
        if self.hp <= 0:
            kill(self.entity)

class Offensive(object):
    def __init__(self,dmg):
        self.dmg = dmg
        self.priority = 0

    def deal_damage(self,event : DealDamage):
        event.amount += self.dmg

class AI(object):
    """Component for AI controlled entities."""
    def __init__(self, entity):
        self.entity = entity
        self.priority = 0

    def act(self, event : Act):
        import movement
        movement.ai_move(self.entity)

class Fatigue(object):
    def __init__(self, value=0):
        self.value = value
        self.priority = 0

    def pay_fatigue(self, event : PayFatigue):
        self.value += event.amount

# Systems

class BlockingSystem(ecs.System):
    """Just for holding blocking entities."""
    def __init__(self):
        ecs.System.__init__(self,[MapPos, Blocking])
        self.active = False

class TurnOrderSystem(ecs.System):
    def __init__(self):
        ecs.System.__init__(self,[Fatigue])

    def process(self, entities):
        #TODO rework this
        if all(entities[0].get(Team)
               == e.get(Team) for e in entities):
            #GAME OVER
            self.game_over(entities[0].get(Team).team_name=="player_team")
        else:
        #end of filth
            actor = min(entities, key=(lambda e: e.get(Fatigue).value))
            print("%s acts." % actor.name)
            actor.handle_event(Act())

    #TODO filth again
    def game_over(self,victory):
        import sdl2
        import input_
        import start
        self.startrendersystem.active  = True
        self.battlerendersystem.active = False
        input_.activate_mode(start.StartMode)
        input_.clear_mode(start.StartMode)
        input_.add_handler(start.StartMode,
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


# transformations

def kill(entity):
    entity.delete(Blocking)
    entity.delete(Fatigue)
    entity.get(res.Graphic).corpsify()
    battle_log.add_msg("%s dies." % entity.name)

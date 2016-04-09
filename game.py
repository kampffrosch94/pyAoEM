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
        ecs.System.__init__(self,[Fatigue,Team])
        self.turn_order = []

    def process(self, entities):
        entities.sort(key=(lambda e: e.get(Fatigue).value))
        self.turn_order = entities

class ActSystem(ecs.System):
    def __init__(self,turn_order_system):
        ecs.System.__init__(self)
        self.turn_order_system = turn_order_system

    def process(self,_):
        turn_order = self.turn_order_system.turn_order
        actor = turn_order[0]
        print("%s turn" % turn_order[0].name)
        actor.handle_event(Act())
        del turn_order[0]
        turn_order.append(actor)
# transformations

def kill(entity):
    entity.delete(Blocking)
    entity.delete(Fatigue)
    entity.get(res.Graphic).corpsify()
    battle_log.add_msg("%s dies." % entity.name)

    #check game over
    entities = entity.world.get_system_entities(TurnOrderSystem)
    if all(entities[0].get(Team) == e.get(Team) for e in entities):
        game_over(entities[0].get(Team).team_name=="player_team")

# transitions
#TODO make a proper game_over screen and cleanup
def game_over(victory):
    import start
    start.activate()

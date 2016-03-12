import game_events
import input_manager

###simple components
class Blocking(object):
    """Only one blocking entity can be at a map_pos."""
    pass

class CorpseGraphic(object):
    def __init__(self,texture):
        self.texture = texture

class Team(object):
    def __init__(self,team_name):
        self.team_name = team_name

    def __eq__(self,other):
        return self.team_name == other.team_name

###Eventhandling components
class Health(object):
    def __init__(self,entity,max_hp):
        self.entity = entity
        self.max_hp = max_hp
        self.hp = max_hp
        self.priority = 0

    def take_damage(self,event : game_events.TakeDamage):
        self.hp -= event.amount
        if self.hp <= 0:
            import game_transformations
            game_transformations.kill(self.entity)

class Offensive(object):
    def __init__(self,dmg):
        self.dmg = dmg
        self.priority = 0

    def deal_damage(self,event : game_events.DealDamage):
        event.amount += self.dmg

class Input(object):
    """Component for Player controlled entities."""
    def __init__(self,entity):
        self.entity = entity
        self.priority = 0 

    def act(self,event : game_events.Act):
        input_manager.controlled_entity = self.entity
        input_manager.handle_event()

class AI(object):
    """Component for AI controlled entities."""
    def __init__(self,entity):
        self.entity = entity
        self.priority = 0 

    def act(self,event : game_events.Act):
        import movement
        movement.ai_move(self.entity)

class Fatigue(object):
    def __init__(self,value=0):
        self.value = value
        self.priority = 0 

    def pay_fatigue(self,event : game_events.PayFatigue):
        self.value += event.amount

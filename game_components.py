import game_events

class Blocking(object):
    """Only one blocking entity can be at a map_pos."""
    pass

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

class Team(object):
    def __init__(self,team_name):
        self.team_name = team_name

    def __eq__(self,other):
        return self.team_name == other.team_name

class CorpseGraphic(object):
    def __init__(self,texture):
        self.texture = texture

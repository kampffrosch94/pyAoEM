import ecs
import res
import battle_log
import utility
from typing import List


# simple components
class Blocking:
    """Only one blocking entity can be at a map_pos."""
    pass


class MapPos(utility.Position):
    """The position of an entity on the map."""


class Team:
    def __init__(self, team_name):
        self.team_name = team_name

    def __eq__(self, other):
        return self.team_name == other.team_name

    def __repr__(self):
        return self.team_name


# Events

class TakeDamage:
    def __init__(self, deal_dmg_event):
        self.amount = deal_dmg_event.amount
        self.handler_name = "take_damage"


class DealDamage:
    def __init__(self, amount=0):
        self.amount = amount
        self.handler_name = "deal_damage"


class GetHealed:
    def __init__(self, amount):
        self.amount = amount
        self.handler_name = "get_healed"


class Act:
    """"Event which says the entity should act."""
    def __init__(self):
        self.handler_name = "act"


class PayFatigue:
    def __init__(self, amount: int):
        self.amount = amount
        self.handler_name = "pay_fatigue"


# Eventhandling components

class Health:
    def __init__(self, entity, max_hp):
        self.entity = entity
        self.max_hp = max_hp
        self.hp = max_hp
        self.priority = 0

    def take_damage(self, event: TakeDamage):
        self.hp -= event.amount
        if self.hp <= 0:
            kill(self.entity)

    def get_healed(self, event: GetHealed):
        self.hp += event.amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def __repr__(self):
        return "%s/%s" % (self.hp, self.max_hp)


class Offensive:
    def __init__(self, dmg):
        self.dmg = dmg
        self.priority = 0

    def deal_damage(self, event: DealDamage):
        event.amount += self.dmg

    def __repr__(self):
        return "dmg: %s" % self.dmg


class AI:
    """Component for AI controlled entities."""

    def __init__(self, entity):
        self.entity = entity
        self.priority = 0

    def act(self, event: Act):
        import movement
        movement.ai_move(self.entity)


class Fatigue:
    def __init__(self, value=0):
        self.value = value
        self.priority = 0

    def pay_fatigue(self, event: PayFatigue):
        self.value += event.amount

    def __repr__(self):
        return "%s" % self.value

    def __eq__(self, other: 'Fatigue'):
        return self.value == other.value


# Systems

class BlockingSystem(ecs.System):
    """Just for holding blocking entities."""

    def process(self, entities):
        raise ReferenceError("BlockingSystem can't process()")

    def __init__(self):
        ecs.System.__init__(self, [MapPos, Blocking])
        self.active = False


class TurnOrderSystem(ecs.System):
    """Orders all the entities which can act in TurnOrder
    the actual turn is executed from the battle.main_loop() in
    active_take_turn()"""
    def __init__(self):
        ecs.System.__init__(self, [Fatigue, Team])

    def process(self, entities):
        entities.sort(key=(lambda e: e.get(Fatigue).value))


# transformations
def active_take_turn(turn_order: List[ecs.Entity]):
    """Lets the actor first in the turnorder act."""
    actor = turn_order[0]
    # TODO debuglog this
    # print("%s turn" % turn_order[0].name)

    # only costly actions end the turn
    start_fatigue = actor.get(Fatigue).value
    while start_fatigue == actor.get(Fatigue).value:
        actor.handle_event(Act())

    # move actor to the end of the turnorder lis
    del turn_order[0]
    turn_order.append(actor)


def kill(entity):
    entity.delete(Blocking)
    entity.delete(Fatigue)
    entity.get(res.Graphic).corpsify()
    battle_log.add_msg("%s dies." % entity.name)

    # check game over
    entities = entity.world.get_system_entities(TurnOrderSystem)
    if all(entities[0].get(Team) == e.get(Team) for e in entities):
        game_over(entities[0].get(Team).team_name == "player_team")


# transitions
# TODO make a proper game_over screen and cleanup
def game_over(victory):
    import game_over
    game_over.activate(victory)

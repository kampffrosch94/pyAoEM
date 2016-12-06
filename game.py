import logging
from typing import List, Iterable, Dict, Tuple, Iterator

import ability
import battle_log
import ecs
import res
import util

game_logger = logging.getLogger("Game")
turn_order_logger = logging.getLogger("TurnOrder")


# simple components
class Blocking:
    """Only one blocking entity can be at a map_pos."""
    pass


class Team:
    def __init__(self, team_name):
        self.team_name = team_name

    def __eq__(self, other):
        return self.team_name == other.team_name

    def __repr__(self):
        return self.team_name


class Dead:
    """Marker for actors that got killed."""
    pass


# Events
class Event:
    def __repr__(self):
        if hasattr(self, "amount"):
            return "%s(amount=%s)" % (self.__class__.__name__, self.amount)
        return "%s()" % self.__class__.__name__


class TakeDamage(Event):
    def __init__(self, deal_dmg_event):
        self.amount = deal_dmg_event.amount
        self.handler_name = "take_damage"


class DealDamage(Event):
    def __init__(self, amount=0):
        self.amount = amount
        self.handler_name = "deal_damage"


class GetHealed(Event):
    def __init__(self, amount):
        self.amount = amount
        self.handler_name = "get_healed"


class Act(Event):
    """"Event which says the entity should act."""

    def __init__(self):
        self.handler_name = "act"


class PayFatigue(Event):
    def __init__(self, amount: int):
        self.amount = amount
        self.handler_name = "pay_fatigue"


# Eventhandling components
class Component:
    def __repr__(self):
        return "%s()" % self.__class__.__name__


class Abilities(Component):
    def __init__(self):
        self.container = []  # type: List[ability.Ability]

    def add(self, ab: ability.Ability):
        self.container.append(ab)


class Health(Component):
    def __init__(self, entity, max_hp):
        self.entity = entity
        self.max_hp = max_hp
        self.hp = max_hp
        self.priority = 0

    def take_damage(self, event: TakeDamage):
        self.hp -= event.amount
        if self.hp <= 0:
            event.amount = abs(self.hp)
            kill(self.entity)
        else:
            event.amount = 0

    def get_healed(self, event: GetHealed):
        self.hp += event.amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def __repr__(self):
        return "%s(%s/%s)" % (self.__class__.__name__, self.hp, self.max_hp)


class Offensive(Component):
    def __init__(self, dmg):
        self.dmg = dmg
        self.priority = 0

    def deal_damage(self, event: DealDamage):
        event.amount += self.dmg

    def __repr__(self):
        return "%s(dmg: %s)" % (self.__class__.__name__, self.dmg)


class Defense(Component):
    def __init__(self, defense: int):
        self.defense = defense
        self.priority = 1

    def take_damage(self, event: TakeDamage):
        event.amount -= self.defense

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.defense)


class Fatigue(Component):
    def __init__(self, value=0):
        self.value = value
        self.priority = 0

    def pay_fatigue(self, event: PayFatigue):
        self.value += event.amount

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.value)

    def __eq__(self, other: 'Fatigue'):
        return self.value == other.value


class Inventory(Component):
    def __init__(self):
        self.items = []  # type: List[ecs.Entity]
        self.priority = 10  # items come before intrinsics

    def add_item(self, item: ecs.Entity):
        self.items.append(item)

    def take_damage(self, event: TakeDamage):
        for item in self.items:
            item.handle_event(event)


# Systems

class BlockingSystem(ecs.System):
    """Just for holding blocking entities."""

    def process(self, entities):
        raise ReferenceError("BlockingSystem can't process()")

    def __init__(self):
        ecs.System.__init__(self, [util.Position, Blocking])
        self.active = False


class TurnOrderSystem(ecs.System):
    """Orders all the entities which can act in TurnOrder
    the actual turn is executed from the battle.main_loop() in
    active_take_turn()"""

    def __init__(self):
        ecs.System.__init__(self, [Fatigue, Team])

    def process(self, entities):
        entities.sort(key=(lambda e: e.get(Fatigue).value))


class DeathSystem(ecs.System):
    """Processes killed entities"""

    def __init__(self):
        ecs.System.__init__(self, [Dead, Blocking, Fatigue])

    def process(self, entities):
        game_logger.debug("Killing: %s" % entities)
        for entity in entities[:]:  # copy cause we modify
            entity.delete(Blocking)
            entity.delete(Fatigue)
            entity.get(res.Graphic).corpsify()
            battle_log.add_msg("%s dies." % entity.name)


# transformations
def active_take_turn(turn_order: List[ecs.Entity]):
    """Lets the actor first in the turnorder act."""
    actor = turn_order[0]
    world = actor.world

    turn_order_logger.debug("%r turn" % turn_order[0].name)

    # only costly actions end the turn
    start_fatigue = actor.get(Fatigue).value
    while (not actor.has(Dead)) and start_fatigue == actor.get(
            Fatigue).value and actor.world.alive:
        turn_order_logger.debug("%r acts" % turn_order[0].name)
        actor.handle_event(Act())
        world.invoke_system(DeathSystem)  # clean up killed actors

    turn_order_logger.debug("%s turn done" % actor)

    # move actor to the end of the turnorder lis
    try:
        turn_order.remove(actor)
        turn_order.append(actor)
    except ValueError:
        # if actor is not in turnorder anymore, do nothing
        pass


def kill(entity):
    entity.set(Dead())


# util
def pos_entity_dict(entities: Iterable[ecs.Entity]) \
        -> Dict[util.Position, ecs.Entity]:
    """Turns list of entities into dict: pos->entity"""
    result = {}  # type: Dict[util.Position, ecs.Entity]
    for e in entities:
        pos = e.get(util.Position)
        if pos in result:
            raise ValueError("Multiple entities with same pos.")
        result[pos] = e
    return result


def compute_enemies(entity: ecs.Entity) -> Iterator[ecs.Entity]:
    world = entity.world
    acting_es = world.get_system_entities(TurnOrderSystem)
    for e in acting_es:
        if not e.get(Team) == entity.get(Team):
            yield e

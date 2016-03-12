from components import MapPos
from game_systems import (BlockingSystem, AttackableSystem,
        TurnOrderSystem)
from game_components import Offensive, Health, Team
from game_events import DealDamage, TakeDamage, PayFatigue
import battle_log
import map_manager
import operator
import utility

def can_move(entity, direction):
    pos = entity.get(MapPos)
    new_pos = pos.copy()
    new_pos.apply_direction(direction)

    if map_manager.current_map.is_wall(new_pos):
        return False

    world = entity.world
    blocking_es = world.get_system_entities(BlockingSystem)
    for e in blocking_es:
        if e.get(MapPos) == new_pos:
            return False
    return True

def move(entity, direction):
    mp = entity.get(MapPos)
    mp.apply_direction(direction)

def get_bump_attackable(entity,direction):
    world = entity.world
    attackable_es = world.get_system_entities(AttackableSystem)
    pos = entity.get(MapPos)
    new_pos = pos.copy()
    new_pos.apply_direction(direction)
    for e in attackable_es:
        if e.get(MapPos) == new_pos:
            return e
    return None

def can_bump_attack(entity, direction):
    if not entity.has(Offensive):
        return False
    target = get_bump_attackable(entity,direction)
    if target == None:
        return False
    elif entity.has(Team) and target.has(Team):
        if entity.get(Team) == target.get(Team):
            return False
    return True

def bump_attack(entity,direction):
    target = get_bump_attackable(entity,direction)
    battle_log.add_msg("%s hits %s." % (entity.name,target.name))
    deal_dmg_event = DealDamage()
    entity.handle_event(deal_dmg_event)
    take_dmg_event = TakeDamage(deal_dmg_event)
    target.handle_event(take_dmg_event)

    #TODO cleanup the following
    print("Target new HP: %s" % target.get(Health).hp)


def attack_or_move(entity,direction):
    if can_move(entity,direction):
        move(entity,direction)
        entity.handle_event(PayFatigue(100))
    elif can_bump_attack(entity,direction):
        bump_attack(entity,direction)
        entity.handle_event(PayFatigue(100))

def ai_move(entity):
    world = entity.world
    acting_es = world.get_system_entities(TurnOrderSystem)
    enemy_pos  = []
    for e in acting_es:
        if not e.get(Team) == entity.get(Team):
            enemy_pos.append(e.get(MapPos).to_tuple())

    d_map = map_manager.current_map.djikstra_map(enemy_pos)
    pos = entity.get(MapPos).to_tuple()
    goal_pos = pos
    for n_pos in map_manager.current_map.neighbors(pos):
        if d_map[goal_pos] > d_map[n_pos]:
            goal_pos = n_pos
    d = tuple(map(operator.sub,goal_pos,pos))
    attack_or_move(entity,utility.Direction(*d))

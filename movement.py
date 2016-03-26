from game_systems import (BlockingSystem, TurnOrderSystem)
from game_components import Offensive, Health, Team
from game_events import DealDamage, TakeDamage, PayFatigue
import battle_log
import map_
import operator
import utility

def get_blocker_at_pos(world,pos):
    blocking_es = world.get_system_entities(BlockingSystem)
    for e in blocking_es:
        if e.get(map_.MapPos).to_tuple() == pos:
            return e
    return None

def is_pos_free(world,pos):
    if map_.current_map.is_wall(pos):
        return False
    target = get_blocker_at_pos(world,pos)
    if not target == None:
        return False
    return True

def attack_or_move(entity,direction):
    """returns True on success, False on failure"""
    pos = entity.get(map_.MapPos)
    new_pos = pos.copy()
    new_pos.apply_direction(direction)
    if map_.current_map.is_wall(new_pos.to_tuple()):
        return False
    target = get_blocker_at_pos(entity.world,new_pos.to_tuple())
    if target == None: #move
        mp = entity.get(map_.MapPos)
        mp.apply_direction(direction)
        entity.handle_event(PayFatigue(100))
        return True
    elif target.has(Health) and not entity.get(Team) == target.get(Team):
        battle_log.add_msg("%s hits %s." % (entity.name,target.name))
        deal_dmg_event = DealDamage()
        entity.handle_event(deal_dmg_event)
        take_dmg_event = TakeDamage(deal_dmg_event)
        target.handle_event(take_dmg_event)
        entity.handle_event(PayFatigue(100))
        return True
    return False

def ai_move(entity):
    world = entity.world
    acting_es = world.get_system_entities(TurnOrderSystem)
    enemy_pos  = []
    for e in acting_es:
        if not e.get(Team) == entity.get(Team):
            enemy_pos.append(e.get(map_.MapPos).to_tuple())

    d_map = map_.current_map.djikstra_map(enemy_pos)
    pos = entity.get(map_.MapPos).to_tuple()
    goal_pos = pos
    for n_pos in map_.current_map.neighbors(pos):
        if d_map[goal_pos] > d_map[n_pos]:
            goal_pos = n_pos
    if goal_pos == pos:
        print("%s waits because it doesn't want to move." % entity.name)
        entity.handle_event(PayFatigue(100))
    else:
        d = tuple(map(operator.sub,goal_pos,pos))
        if not attack_or_move(entity,utility.Direction(*d)):
            print("%s waits because it can't move." % entity.name)
            entity.handle_event(PayFatigue(100))

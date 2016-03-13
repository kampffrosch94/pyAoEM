from components import MapPos
from game_systems import (BlockingSystem, TurnOrderSystem)
from game_components import Offensive, Health, Team
from game_events import DealDamage, TakeDamage, PayFatigue
import battle_log
import map_manager
import operator
import utility

def get_entity_at_pos(world,pos):
    blocking_es = world.get_system_entities(BlockingSystem)
    for e in blocking_es:
        if e.get(MapPos) == pos:
            return e
    return None

def attack_or_move(entity,direction):
    """returns True on success, False on failure"""
    pos = entity.get(MapPos)
    new_pos = pos.copy()
    new_pos.apply_direction(direction)
    if map_manager.current_map.is_wall(new_pos):
        return False
    target = get_entity_at_pos(entity.world,new_pos)
    if target == None: #move
        mp = entity.get(MapPos)
        mp.apply_direction(direction)
        entity.handle_event(PayFatigue(100))
        return True
    elif target.has(Health):
        battle_log.add_msg("%s hits %s." % (entity.name,target.name))
        deal_dmg_event = DealDamage()
        entity.handle_event(deal_dmg_event)
        take_dmg_event = TakeDamage(deal_dmg_event)
        target.handle_event(take_dmg_event)
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
    if goal_pos == pos:
        print("%s waits." % entity.name)
        e.handle_event(PayFatigue(100))
    else:
        d = tuple(map(operator.sub,goal_pos,pos))
        attack_or_move(entity,utility.Direction(*d))

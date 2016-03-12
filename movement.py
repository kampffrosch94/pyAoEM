from components import MapPos
from game_systems import BlockingSystem, AttackableSystem
from game_components import Offensive, Health, Team
from game_events import DealDamage, TakeDamage
import battle_log
import map_manager

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

import operator

import battle_log
import ecs
import game
import map_
import utility


def get_blocker_at_pos(world: ecs.World, pos: utility.Position) -> ecs.Entity:
    blocking_es = world.get_system_entities(game.BlockingSystem)
    for e in blocking_es:
        if e.get(game.MapPos).to_tuple() == pos:
            return e
    return None


def pos_is_free(world: ecs.World, pos: utility.Position) -> bool:
    if map_.current_map.is_wall(pos):
        return False
    target = get_blocker_at_pos(world, pos)
    if target is not None:
        return False
    return True


def attack_or_move(entity: ecs.Entity, direction: utility.Direction) -> bool:
    """returns True on success, False on failure"""
    pos = entity.get(game.MapPos)
    new_pos = pos.copy()
    new_pos.move(direction)
    if map_.current_map.is_wall(new_pos):
        return False
    target = get_blocker_at_pos(entity.world, new_pos)
    if target is None:  # move
        mp = entity.get(game.MapPos)
        mp.move(direction)
        entity.handle_event(game.PayFatigue(100))
        return True
    elif target.has(game.Health) and not entity.get(game.Team) == target.get(game.Team):
        battle_log.add_msg("%s hits %s." % (entity.name, target.name))
        deal_dmg_event = game.DealDamage()
        entity.handle_event(deal_dmg_event)
        take_dmg_event = game.TakeDamage(deal_dmg_event)
        target.handle_event(take_dmg_event)
        entity.handle_event(game.PayFatigue(100))
        return True
    return False


def ai_move(entity: ecs.Entity) -> None:
    world = entity.world
    team = entity.get(game.Team)
    acting_es = world.get_system_entities(game.TurnOrderSystem)
    enemy_pos = []
    for e in acting_es:
        if not e.get(game.Team) == entity.get(game.Team):
            enemy_pos.append(e.get(game.MapPos).to_tuple())

    d_map = map_.current_map.djikstra_map(enemy_pos)
    pos = entity.get(game.MapPos).to_tuple()
    d_map[pos] += 1  # don't stand around if you can help it
    goal_pos = pos
    # neighbors doesn't include walls
    for n_pos in map_.current_map.neighbors(pos):
        if d_map[goal_pos] > d_map[n_pos]:
            if pos_is_free(world, n_pos):
                goal_pos = n_pos
            else:
                blocker = get_blocker_at_pos(world, n_pos)
                if blocker.get(game.Team) != team:
                    goal_pos = n_pos

    if goal_pos == pos:
        print("%s waits because it doesn't want to move." % entity.name)
        entity.handle_event(game.PayFatigue(100))
    else:
        d = tuple(map(operator.sub, goal_pos, pos))
        if not attack_or_move(entity, utility.Direction(*d)):
            print("%s waits because it can't move." % entity.name)
            entity.handle_event(game.PayFatigue(100))

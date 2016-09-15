import battle_log
import ecs
import game
import util


def get_blocker_at_pos(world: ecs.World, pos: util.Position) -> ecs.Entity:
    blocking_es = world.get_system_entities(game.BlockingSystem)
    for e in blocking_es:
        if e.get(util.Position).to_tuple() == pos:
            return e
    return None


def pos_is_free(world: ecs.World, pos: util.Position) -> bool:
    if world.map.is_wall(pos):
        return False
    target = get_blocker_at_pos(world, pos)
    if target is not None:
        return False
    return True


def attack_or_move(entity: ecs.Entity, direction: util.Direction) -> bool:
    """returns True on success, False on failure"""
    world = entity.world
    pos = entity.get(util.Position)  # type: util.Position
    new_pos = pos.copy().move(direction)

    if world.map.is_wall(new_pos):
        return False
    target = get_blocker_at_pos(entity.world, new_pos)
    if target is None:  # move
        mp = entity.get(util.Position)
        mp.move(direction)
        return True
    elif target.has(game.Health) and not entity.get(game.Team) == target.get(game.Team):
        battle_log.add_msg("%s hits %s." % (entity.name, target.name))
        deal_dmg_event = game.DealDamage()
        entity.handle_event(deal_dmg_event)
        take_dmg_event = game.TakeDamage(deal_dmg_event)
        target.handle_event(take_dmg_event)
        return True
    return False

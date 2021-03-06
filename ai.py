import operator
import logging

import ability
import ecs
import game
import movement
import util
from game import Component, Act

logger = logging.getLogger("AI")


class AI(Component):
    """Component for AI controlled entities."""

    def __init__(self, entity: ecs.Entity):
        self.entity = entity
        self.priority = 0

    def act(self, _: Act):
        e = self.entity
        logger.debug("%s is thinking." % e)
        world = e.world  # type: ecs.World
        e_pos = e.get(util.Position)
        # TODO decide wether to activate an ability or move
        abilities = e.get(ability.Abilities).container
        blocking_es = world.get_system_entities(game.BlockingSystem)
        enemies = game.compute_enemies(e)
        for g_pos, enemy in game.pos_entity_dict(enemies).items():
            for ab in abilities:
                if ab.in_range(world.map, blocking_es, e_pos, g_pos):
                    ab.fire(world.map, blocking_es, e, g_pos)
                    return
        ai_move(e)


def ai_move(entity: ecs.Entity) -> None:
    world = entity.world
    team = entity.get(game.Team)

    enemy_pos = [e.get(util.Position).to_tuple() for e in
                 game.compute_enemies(entity)]

    d_map = world.map.djikstra_map(enemy_pos)
    pos = entity.get(util.Position).to_tuple()
    d_map[pos] += 1  # don't stand around if you can help it
    goal_pos = pos
    # neighbors doesn't include walls
    for n_pos in world.map.neighbors(pos):
        if d_map[goal_pos] > d_map[n_pos]:
            if movement.pos_is_free(world, n_pos):
                goal_pos = n_pos
            else:
                blocker = movement.get_blocker_at_pos(world, n_pos)
                if blocker.get(game.Team) != team:
                    goal_pos = n_pos

    if goal_pos == pos:
        print("%s waits because it doesn't want to move." % entity.name)
    else:
        d = tuple(map(operator.sub, goal_pos, pos))
        if not movement.attack_or_move(entity, util.Direction(*d)):
            print("%s waits because it can't move." % entity.name)
    entity.handle_event(game.PayFatigue(100))


class Idler(Component):
    """Component for AI controlled entities."""

    def __init__(self, entity: ecs.Entity):
        self.entity = entity
        self.priority = 0

    def act(self, _: Act):
        self.entity.handle_event(game.PayFatigue(100))

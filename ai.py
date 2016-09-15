import operator

import ecs
import game
import util
from game import Component, Act
import movement


class AI(Component):
    """Component for AI controlled entities."""

    def __init__(self, entity):
        self.entity = entity
        self.priority = 0

    def act(self, _: Act):
        ai_move(self.entity)


def ai_move(entity: ecs.Entity) -> None:
    world = entity.world
    team = entity.get(game.Team)
    acting_es = world.get_system_entities(game.TurnOrderSystem)
    enemy_pos = []
    for e in acting_es:
        if not e.get(game.Team) == entity.get(game.Team):
            enemy_pos.append(e.get(util.Position).to_tuple())

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
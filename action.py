import attr

import ecs
import util
import ability
import game


@attr.s
class Controller:
    planner = attr.ib()
    priority = attr.ib(init=False, default=0)

    # noinspection PyUnresolvedReferences
    def act(self, _):
        self.planner.plan_action().execute()


@attr.s
class MovementAction:
    user = attr.ib()  # type: ecs.Entity
    direction = attr.ib()  # type: util.Direction

    def execute(self):
        pos = self.user.get(util.Position)  # type: util.Position
        pos.move(self.direction)



@attr.s
class StandardAction:
    user = attr.ib()  # type: ecs.Entity
    abil = attr.ib()  # type: ability.Ability
    target_pos = attr.ib()  # type: util.Position

    def execute(self):
        world = self.user.world
        actors = world.get_system_entities(game.TurnOrderSystem)
        self.abil.fire(world.map, actors, self.user, self.target_pos)


@attr.s
class ActionManager:
    """Ensures uniform actionpointrules."""
    move_points = attr.ib(init=False, default=1)
    action_points = attr.ib(init=False, default=1)

    def standard_action(self):
        if self.action_points <= 0:
            raise RuntimeError("No action points left.")
        else:
            self.move_points -= 1
            return StandardAction()

    def movement_action(self):
        if self.move_points <= 0:
            if self.action_points <= 0:
                raise RuntimeError("No action points left.")
            else:
                self.action_points -= 1
        else:
            self.move_points -= 1
        return MovementAction()

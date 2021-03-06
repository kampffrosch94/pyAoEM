from typing import Callable, List, Dict, Optional

import yaml

import ability
import animation
import ecs
import game
import map_
import movement
import res
import util
from game import Component


class Ability:
    def __init__(self,
                 name: str,
                 range_: int,
                 unlock_cost: int,
                 targeting_f: Callable[
                     [map_.TileMap,
                      List[ecs.Entity],
                      util.Position,
                      util.Position],
                     List[util.Position]],
                 effects: List['Effect'],
                 animation_g: Optional[res.Graphic]) -> None:
        self.name = name
        self.range_ = range_
        self.target = targeting_f
        assert len(effects) is not 0
        self._effects = effects
        self.animation_g = animation_g or res.load_graphic("todo")
        self.unlock_cost = unlock_cost

    def __repr__(self):
        return "\n %s : %s\n Range: %s\n Targeting_f: %s\n Effects: \n   %s" % (
            self.__class__.__name__,
            self.name,
            self.range_,
            self.target,
            self._effects)

    def fire(self,
             tmap: map_.TileMap,
             relevant_entities: List[ecs.Entity],
             user: ecs.Entity,
             goal_pos: util.Position) -> None:
        target_poss = self.target(tmap, relevant_entities,
                                  user.get(util.Position),
                                  goal_pos)

        for effect in self._effects:
            # send copy of relevant_entities, else one dies and vanishes
            # from the list while it is iterated over
            effect.fire(tmap, user, relevant_entities[:], target_poss)

        user.world.animation_q.append(
            animation.Animation(self.animation_g, target_poss))

    def in_range(self, tmap: map_.TileMap, relevant_entities: List[ecs.Entity],
                 user_pos: util.Position, goal_pos: util.Position):
        if user_pos.distance(goal_pos) <= self.range_:
            target_poss = self.target(tmap, relevant_entities,
                                      user_pos,
                                      goal_pos)
            if goal_pos in target_poss:
                return True
        return False


# noinspection PyUnusedLocal
def _smite_target_f(tmap: map_.TileMap,
                    relevant_entities: List[ecs.Entity],
                    user_pos: util.Position,
                    goal_pos: util.Position
                    ) -> List[util.Position]:
    return [goal_pos]


# noinspection PyUnusedLocal
def _line_target_f(tmap: map_.TileMap,
                   relevant_entities: List[ecs.Entity],
                   user_pos: util.Position,
                   goal_pos: util.Position
                   ) -> List[util.Position]:
    line = user_pos.line_to(goal_pos)
    return line[1:]


# noinspection PyUnusedLocal
def _fly_target_f(tmap: map_.TileMap,
                  relevant_entities: List[ecs.Entity],
                  user_pos: util.Position,
                  goal_pos: util.Position
                  ) -> List[util.Position]:
    line = user_pos.line_to(goal_pos)
    line_to_first_blocking = []
    entity_dict = game.pos_entity_dict(relevant_entities)
    for pos in line[1:]:
        line_to_first_blocking.append(pos)
        if tmap.is_wall(pos) or (
                        pos in entity_dict and entity_dict[pos].has(
                    game.Blocking)):
            break
    return line_to_first_blocking


def _create_aoe_smite_f(spread: int):
    # noinspection PyUnusedLocal
    def aoe_smite_target_f(tmap: map_.TileMap,
                           relevant_entities: List[ecs.Entity],
                           user_pos: util.Position,
                           goal_pos: util.Position
                           ) -> List[util.Position]:
        result = [goal_pos]  # type: List[util.Position]
        for r in range(1, spread + 1):
            result.extend(goal_pos.circle(r))
        return result

    return aoe_smite_target_f


def _parse_target_f(ability_data):
    if "blast" in ability_data:
        pass
        return None, None
    elif "flood_fill" in ability_data:
        pass
        return None, None
    elif "line" in ability_data:
        return _line_target_f, ability_data["range"]
    elif "spread" in ability_data:
        pass
        return None, None
    elif "fly" in ability_data:
        if "radius" in ability_data:  # maybe add radius as wrapper_f
            pass
            return None, None
        else:
            return _fly_target_f, ability_data["range"]
    else:  # regular old smite targeting
        if "radius" in ability_data:
            return _create_aoe_smite_f(ability_data["radius"]), ability_data[
                "range"]
        else:
            return _smite_target_f, ability_data["range"]


class Effect:
    def fire(self, tmap, user, relevant_entities, target_poss):
        raise NotImplementedError()

    def __repr__(self):
        return "%s" % self.__class__.__name__


class HealEffect(Effect):
    def __init__(self, effect_data):
        if "base" in effect_data:
            self.base = effect_data["base"]
        else:
            self.base = 0
        if "scaling" in effect_data:
            self.scaling = effect_data["scaling"]
        else:
            self.scaling = 0

    def fire(self, tmap, user, relevant_entities, target_poss):
        for e in relevant_entities:
            if e.get(util.Position).to_tuple() in target_poss:
                # use dmg stats for now TODO change later
                dmg_ev = game.DealDamage()
                user.handle_event(dmg_ev)
                heal_amount = self.scaling * dmg_ev.amount + self.base
                e.handle_event(game.GetHealed(heal_amount))

    def __repr__(self):
        return "%s: Base: %s Scaling: %s" % (self.__class__.__name__,
                                             self.base, self.scaling)


class DmgEffect(Effect):
    def __init__(self, effect_data):
        if "base" in effect_data:
            self.base = effect_data["base"]
        else:
            self.base = 0
        if "scaling" in effect_data:
            self.scaling = effect_data["scaling"]
        else:
            self.scaling = 0

    def __repr__(self):
        return "%s: Base: %s Scaling: %s" % (self.__class__.__name__,
                                             self.base, self.scaling)

    # noinspection PyUnusedLocal
    def fire(self, tmap, user, relevant_entities,
             target_poss: List[util.Position]):
        for e in relevant_entities:
            if e.get(util.Position) in target_poss:
                dmg_ev = game.DealDamage()
                user.handle_event(dmg_ev)
                dmg_ev.amount *= self.scaling
                dmg_ev.amount += self.base
                # Todo remove the following debug line
                print("Deal damage to: %s" % e.name)
                e.handle_event(game.TakeDamage(dmg_ev))


class MoveEffect(Effect):
    def __init__(self, effect_data):
        pass

    def fire(self, tmap, user: ecs.Entity, relevant_entities,
             target_poss: List[util.Position]):
        user_pos = user.get(util.Position)  # type: util.Position
        for t_pos in target_poss:
            d = user_pos.direction_to(t_pos)
            movement.attack_or_move(user, d)

    def __repr__(self):
        return "%s" % self.__class__.__name__


class FatigueCostEffect(Effect):
    """Effect which makes the user pay Fatigue for the used Ability"""

    def __init__(self, cost: int):
        self.cost = cost

    def __repr__(self):
        return "%s: Cost: %s" % (self.__class__.__name__, self.cost)

    # noinspection PyUnusedLocal
    def fire(self, tmap, user: ecs.Entity, relevant_entities, target_poss):
        user.handle_event(game.PayFatigue(self.cost))


def _parse_effects(ability_data: Dict[str, object]
                   ) -> List[Effect]:
    effects = []  # type: List[Effect]
    for name, effect_data in ability_data.items():
        if name == "heal":
            assert isinstance(effect_data, dict)
            effects.append(HealEffect(effect_data))
        elif name == "dmg":
            assert isinstance(effect_data, dict)
            effects.append(DmgEffect(effect_data))
        elif name == "move":
            effects.append(MoveEffect(effect_data))
        elif name == "fatigue_cost":
            assert isinstance(effect_data, int)
            effects.append(FatigueCostEffect(effect_data))
            # else no recognized effect => ignore
    return effects


def _parse_abilities(abilities_data: Dict[str, Dict[str, object]]
                     ) -> Dict[str, Ability]:
    parsed_abilities = {}
    for name, ability_data in abilities_data.items():
        # find out what kind of targeting method this ability uses
        # and the range while we are at it
        targeting_f, range_ = _parse_target_f(ability_data)
        if targeting_f is None:
            continue  # TODO this is not finished

        # find out which effects (plural) the ability has
        effects = _parse_effects(ability_data)

        animation_g = None
        if "animation" in ability_data:
            animation_g = res.load_graphic(ability_data["animation"])

        unlock_cost = ability_data['unlock_cost']  # type: int

        parsed_abilities[name] = Ability(name, range_, unlock_cost, targeting_f,
                                         effects,
                                         animation_g)

    return parsed_abilities


with open("ability/abilities.yaml", "r") as f:
    _abilities_data = yaml.load(f)

abilities = _parse_abilities(_abilities_data)


class Abilities(Component):
    def __init__(self):
        self.container = []  # type: List[ability.Ability]

    def add(self, ab: Ability):
        self.container.append(ab)

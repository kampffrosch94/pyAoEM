import json

import game
import map_
import utility as util
import ecs

from typing import Callable, List, Dict


class Ability:
    def __init__(self,
                 name: str,
                 range_: int,
                 targeting_f: Callable[
                     [map_.TileMap,
                      List[ecs.Entity],
                      util.Position,
                      util.Position],
                     List[util.Position]],
                 effects: List['Effect']) -> None:
        self.name = name
        self.range_ = range_
        self.target = targeting_f
        assert len(effects) is not 0
        self._effects = effects

    def fire(self,
             tmap: map_.TileMap,
             relevant_entities: List[ecs.Entity],
             user: ecs.Entity,
             goal_pos: util.Position) -> None:
        target_poss = self.target(tmap, relevant_entities,
                                  user.get(game.MapPos),
                                  goal_pos)

        for effect in self._effects:
            # send copy of relevant_entities, else one dies and vanishes
            # from the list while it is iterated over
            effect.fire(tmap, user, relevant_entities[:], target_poss)

    def __repr__(self):
        return "\n %s : %s\n Range: %s\n Targeting_f: %s\n Effects: \n   %s" % (
            self.__class__.__name__,
            self.name,
            self.range_,
            self.target,
            self._effects)


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
    entity_dict = map_.pos_entity_dict(relevant_entities)
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
        # TODO use Position.circle() here
        raise NotImplementedError

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
            return None, None
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
            if e.get(game.MapPos).to_tuple() in target_poss:
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
            if e.get(game.MapPos) in target_poss:
                dmg_ev = game.DealDamage()
                user.handle_event(dmg_ev)
                dmg_ev.amount *= self.scaling
                dmg_ev.amount += self.base
                # Todo remove the following debug line
                print("Deal damage to: %s" % e.name)
                e.handle_event(game.TakeDamage(dmg_ev))


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
        parsed_abilities[name] = Ability(name, range_, targeting_f, effects)

    return parsed_abilities


with open("ability/abilities.json", "r") as f:
    _abilities_data = json.load(f)

abilities = _parse_abilities(_abilities_data)

# TODO remove debug code or better log this
import pprint

pprint.pprint(abilities)

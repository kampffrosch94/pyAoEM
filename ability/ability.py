import json
import utility
import game

class Ability:
    def __init__(self, name, range_, targeting_f, effects):
        self.name = name
        self.range_ = range_
        self.target = targeting_f
        self._effects = effects

    def target(self, map_, user_pos, goal_pos):
        raise NotImplementedError("Override this Method.")

    def fire(self, map_, relevant_entities, user, goal_pos):
        target_poss = self.target(map_, user.get(game.MapPos).to_tuple(),
                                  goal_pos.to_tuple())

        for effect in self._effects:
            # send copy of relevant_entities, else one dies and vanishes
            # from the list while it is iterated over
            effect.fire(map_, user, relevant_entities[:], target_poss)

    def __repr__(self):
        return "\n %s : %s\n Range: %s\n Targeting_f: %s\n Effects: \n   %s" % (
            self.__class__.__name__,
            self.name,
            self.range_,
            self.target,
            self._effects)

def _smite_target_f(map_, user_pos, goal_pos):
    return [goal_pos]

def _line_target_f(map_, user_pos, goal_pos):
    line = utility.get_line(user_pos, goal_pos)
    return line[1:]

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
        if "radius" in ability_data: #maybe add radius as wrapper_f
            pass
            return None, None
        else:
            pass
            return None, None
    else: #regular old smite targeting
        if "radius" in ability_data:
            return None, None
        else:
            return _smite_target_f, ability_data["range"]

class Effect:
    def fire(self, map_, relevant_entities, target_poss):
        raise NotImplementedError()

    def __repr__(self):
        return "%s" % self.__class__.__name__

class HealEffect:
    def __init__(self, effect_data):
        if "base" in effect_data:
            self.base = effect_data["base"]
        else:
            self.base = 0
        if "scaling" in effect_data:
            self.scaling = effect_data["scaling"]
        else:
            self.scaling = 0

    def fire(self, map_, user, relevant_entities, target_poss):
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

class DmgEffect:
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

    def fire(self, map_, user, relevant_entities, target_poss):
        for e in relevant_entities:
            if e.get(game.MapPos).to_tuple() in target_poss:
                dmg_ev = game.DealDamage()
                user.handle_event(dmg_ev)
                dmg_ev.amount *= self.scaling
                dmg_ev.amount += self.base
                e.handle_event(game.TakeDamage(dmg_ev))
                print("DMG to: %s" % e.name)

def _parse_effects(ability_data):
    effects = []
    for name, effect_data in ability_data.items():
        if name == "heal":
            effects.append(HealEffect(effect_data))
        elif name == "dmg":
            effects.append(DmgEffect(effect_data))
        # else no recognized effect
    return effects

def _parse_abilities(abilities_data):
    abilities = {}
    for name, ability_data in abilities_data.items():
        # find out what kind of targeting method this ability uses
        # and the range while we are at it
        targeting_f, range_ = _parse_target_f(ability_data)
        if targeting_f is None:
            continue # TODO this is not finished

        # find out which effects (plural) the ability has
        effects = _parse_effects(ability_data)
        abilities[name] = Ability(name, range_, targeting_f, effects)
        
    return abilities

with open("ability/abilities.json","r") as f:
    _abilities_data = json.load(f)

abilities = _parse_abilities(_abilities_data)
if __name__ == "__main__":
    import pprint
    pprint.pprint(abilities)

import battle
import ecs
import res
import util
from game import (Health, Blocking, Offensive, Fatigue, Team, AI)

world = None  # type: ecs.World


def create_creature(name, texture, pos, mhp, dmg):
    creature = ecs.Entity(world)
    creature.name = name

    pos_x, pos_y = pos
    creature.set(util.Position(pos_x, pos_y))
    creature.set(res.load_graphic(texture))

    creature.set(Blocking())
    creature.set(Health(creature, mhp))
    creature.set(Offensive(dmg))
    creature.set(Fatigue())
    return creature


def create_player_creature(name, texture, pos, mhp, dmg):
    pc = create_creature(name, texture, pos, mhp, dmg)
    pc.set(Team("player_team"))
    pc.set(battle.Input(pc))
    return pc


def create_ai_creature(name, texture, pos, mhp, dmg):
    ac = create_creature(name, texture, pos, mhp, dmg)
    ac.set(Team("team monster"))
    ac.set(AI(ac))
    return ac

import battle
import ecs
import game
import res
import util
from game import (Health, Blocking, Offensive, Fatigue, Team, Inventory,
                  Defense)
from ability import Abilities
from ai import AI, Idler

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
    creature.set(Abilities())
    return creature


def create_player_creature(name, texture, pos, mhp, dmg):
    pc = create_creature(name, texture, pos, mhp, dmg)
    pc.set(Team("player_team"))
    pc.set(battle.Input(pc))

    test_armour = ecs.Entity(world)
    g = res.load_graphic("armour_gold_dragon")
    g.z = 1
    test_armour.set(g)
    test_armour.set(game.BoundPosition(pc))
    test_armour.set(util.Position(0, 0))
    test_armour.set(Defense(1))

    inv = Inventory()
    inv.add_item(test_armour)
    pc.set(inv)

    return pc


def create_ai_creature(name, texture, pos, mhp, dmg):
    ac = create_creature(name, texture, pos, mhp, dmg)
    ac.set(Team("team monster"))
    ac.set(AI(ac))
    ac.set(game.Loot(100))
    return ac


def create_idler(name, texture, pos, mhp, dmg):
    ac = create_creature(name, texture, pos, mhp, dmg)
    ac.set(Team("team monster"))
    ac.set(Idler(ac))
    ac.set(game.Loot(100))
    return ac

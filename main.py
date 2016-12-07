import logging
import random

import battle
import battle_log
import ecs
import factory
import game
import input_
import map_
import movement
import start
import util
import ability

logging.basicConfig(filename="logs/main.log", level=logging.DEBUG, filemode="w")

world = ecs.World()

world.add_system(game.BlockingSystem())

world.add_system(battle.EntityRenderSystem())
world.add_system(game.TurnOrderSystem())
world.add_system(battle.HealthRenderSystem(world))
world.add_system(game.BoundPositionSystem())
world.add_system(game.DeathSystem())
world.add_system(game.LootSystem())

factory.world = world

player_number = 3  # random.randint(1, 3)
enemy_number = random.randint(5, 8)
pcs = []
enemies = []

abils = list(ability.abilities.values())

for i in range(player_number):
    player_char = factory.create_player_creature(
        name="Player " + str(i + 1),
        texture="human_m",
        pos=(2, 2),
        mhp=10,
        dmg=2)

    abc = player_char.get(game.Abilities)  # type: game.Abilities
    ab_count = random.randint(1, len(abils))
    picks = set()
    for x in range(ab_count):
        picks.add(random.randint(0, len(abils) - 1))
    #for p in picks:
    for p in range(len(abils)):
        abc.add(abils[p])

    pcs.append(player_char)

for i in range(enemy_number):
    enemy = factory.create_ai_creature(
        name="giant newt " + str(i + 1),
        texture="newt",
        pos=(15, 10),
        mhp=5,
        dmg=2)
    abe = enemy.get(game.Abilities)
    abe.add(ability.abilities["rush"])
    enemies.append(enemy)

map_w, map_h = 20, 15
wall_chance = 42
world.map = map_.TileMap(map_w, map_h, wall_chance)

# place the actors TODO make this a function
pos_list = [x for x in world.map.wall_map]
pos_list.sort(key=(lambda pos: pos[0] * map_w + pos[1]))
for pos in pos_list:
    if len(pcs) == 0:
        break
    if movement.pos_is_free(world, pos):
        e = pcs.pop()
        mp = e.get(util.Position)
        mp.x, mp.y = pos
pos_list.reverse()
for pos in pos_list:
    if len(enemies) == 0:
        break
    if movement.pos_is_free(world, pos):
        e = enemies.pop()
        mp = e.get(util.Position)
        mp.x, mp.y = pos


def end_world():
    world.end()


input_.quit_handler = end_world

start.activate(world)


def main():
    battle_log.add_msg("Welcome to AoEM.")
    while world.alive:
        world.main_loop()
    world.destroy()


if __name__ == "__main__":
    main()

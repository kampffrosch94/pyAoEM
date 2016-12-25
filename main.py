import logging
import random

import ability.ability
import battle
import battle_log
import ecs
import factory
import game
import input_
import map_
import start

logging.basicConfig(filename="logs/main.log", level=logging.DEBUG, filemode="w")

# init
world = ecs.World()

world.add_system(game.BlockingSystem())

world.add_system(battle.EntityRenderSystem())
world.add_system(game.TurnOrderSystem())
world.add_system(battle.HealthRenderSystem(world))
world.add_system(game.BoundPositionSystem())
world.add_system(game.DeathSystem())
world.add_system(game.LootSystem(world.base))

factory.world = world


def end_world():
    world.end()


input_.quit_handler = end_world

# new game data
player_number = 3  # random.randint(1, 3)

for i in range(player_number):
    player_char = factory.create_player_creature(
        name="Player " + str(i + 1),
        texture="human_m",
        pos=(2, 2),
        mhp=10,
        dmg=2)  # 2 seems alright

map_w, map_h = 20, 15
wall_chance = 42
world.map = map_.TileMap(map_w, map_h, wall_chance)

world.base.gold = 1000  # start gold

start.activate(world)  # init first scene


def main():
    battle_log.add_msg("Welcome to AoEM.")
    while world.alive:
        world.main_loop()
    world.destroy()


if __name__ == "__main__":
    main()

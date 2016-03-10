from utility import Direction
from movement import can_move, move, can_bump_attack,bump_attack
import input_manager
from input_manager import BattleMode
from game_events import PayFatigue
from sdl2 import SDLK_l, SDLK_h, SDLK_k, SDLK_j


def attack_or_move(entity,direction):
    if can_move(entity,direction):
        move(entity,direction)
        entity.handle_event(PayFatigue(100))
    elif can_bump_attack(entity,direction):
        bump_attack(entity,direction)
        entity.handle_event(PayFatigue(200))

def move_right():
    player_char = input_manager.controlled_entity
    d = Direction(1,0)
    attack_or_move(player_char,d)
def move_left():
    player_char = input_manager.controlled_entity
    d = Direction(-1,0)
    attack_or_move(player_char,d)
def move_up():
    player_char = input_manager.controlled_entity
    d = Direction(0,-1)
    attack_or_move(player_char,d)
def move_down():
    player_char = input_manager.controlled_entity
    d = Direction(0,1)
    attack_or_move(player_char,d)

input_manager.add_handler(BattleMode,move_right,SDLK_l)
input_manager.add_handler(BattleMode,move_left,SDLK_h)
input_manager.add_handler(BattleMode,move_up  ,SDLK_k)
input_manager.add_handler(BattleMode,move_down,SDLK_j)

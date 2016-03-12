from utility import Direction
from movement import (can_move, move, can_bump_attack,bump_attack,
        attack_or_move)
import input_manager
from input_manager import BattleMode
from sdl2 import SDLK_l, SDLK_h, SDLK_k, SDLK_j, SDLK_PERIOD
from game_events import PayFatigue

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
def wait():
    player_char = input_manager.controlled_entity
    player_char.handle_event(PayFatigue(100))

input_manager.add_handler(BattleMode,move_right,SDLK_l)
input_manager.add_handler(BattleMode,move_left,SDLK_h)
input_manager.add_handler(BattleMode,move_up  ,SDLK_k)
input_manager.add_handler(BattleMode,move_down,SDLK_j)
input_manager.add_handler(BattleMode,wait,SDLK_PERIOD)

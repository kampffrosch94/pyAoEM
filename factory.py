from ecs import Entity
from components import (Graphic, MapPos, BattleBuffer)
from game_components import (Health,Blocking,CorpseGraphic,Offensive,
        Fatigue,Team,Input,AI)
import sdl_manager

world = None

def create_creature(name,texture,pos,mhp,dmg,corpsetexture=None):
    creature = Entity(world)
    creature.name = name

    pos_x,pos_y = pos
    creature.set(MapPos(pos_x,pos_y))
    texture = sdl_manager.load_texture(texture)
    creature.set(Graphic(texture))
    creature.set(BattleBuffer())

    creature.set(Blocking())
    creature.set(Health(creature,mhp))
    creature.set(Offensive(dmg))
    creature.set(Fatigue())
    if corpsetexture:
        corpsetexture = sdl_manager.load_texture(corpsetexture)
        creature.set(CorpseGraphic(corpsetexture))
    return creature

def create_player_creature(name,texture,pos,mhp,dmg,corpsetexture=None):
    pc = create_creature(name,texture,pos,mhp,dmg,corpsetexture)
    pc.set(Team("player_team"))
    pc.set(Input(pc))
    return pc

def create_ai_creature(name,texture,pos,mhp,dmg,corpsetexture=None):
    ac = create_creature(name,texture,pos,mhp,dmg,corpsetexture)
    ac.set(Team("team monster"))
    ac.set(AI(ac))
    return ac

from ecs import Entity
from game_components import (Health,Blocking,CorpseGraphic,Offensive,
        Fatigue,Team,AI)
import res
import input_
import map_manager
import battle

world = None

def create_creature(name,texture,pos,mhp,dmg,corpsetexture=None):
    creature = Entity(world)
    creature.name = name

    pos_x,pos_y = pos
    creature.set(map_manager.MapPos(pos_x,pos_y))
    creature.set(res.load_graphic(texture))
    creature.set(battle.BattleBuffer())

    creature.set(Blocking())
    creature.set(Health(creature,mhp))
    creature.set(Offensive(dmg))
    creature.set(Fatigue())
    if corpsetexture:
        creature.set(CorpseGraphic(res.load_graphic(corpsetexture)))
    return creature

def create_player_creature(name,texture,pos,mhp,dmg,corpsetexture=None):
    pc = create_creature(name,texture,pos,mhp,dmg,corpsetexture)
    pc.set(Team("player_team"))
    pc.set(input_.Input(pc))
    return pc

def create_ai_creature(name,texture,pos,mhp,dmg,corpsetexture=None):
    ac = create_creature(name,texture,pos,mhp,dmg,corpsetexture)
    ac.set(Team("team monster"))
    ac.set(AI(ac))
    return ac

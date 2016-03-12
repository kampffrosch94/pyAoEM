from components import Graphic
from game_components import Blocking, CorpseGraphic,Fatigue
import battle_log

def kill(entity):
    entity.delete(Blocking)
    entity.delete(Fatigue)
    battle_log.add_msg("%s dies." % entity.name)
    if entity.has(CorpseGraphic):
        g  = entity.get(Graphic)
        cg = entity.get(CorpseGraphic)
        g.texture = cg.texture
        g.z = 0
        entity.delete(CorpseGraphic)
    else:
        entity.delete(Graphic)

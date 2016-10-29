import res
import util
from typing import Iterable


class Animation:
    def __init__(self,
                 graphic: res.Graphic,
                 positions: Iterable[util.Position]):
        self.graphic = graphic
        self.positions = positions

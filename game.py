from direct.showbase.ShowBase import ShowBase

from mapmanager import Mapmanager
from player import Player, Position
from conf import PATH_LAND


class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.land = Mapmanager()
        x,y = self.land.load_land(PATH_LAND)
        self.hero = Player(Position(x // 2, y // 2, 2), self.land)
        base.camLens.setFov(90)

import game.unit
import game.util


class Player(game.unit.Unit):
    def __init__(self, x, y, width, height, speed):
        super(Player, self).__init__(x, y, width, height, speed)

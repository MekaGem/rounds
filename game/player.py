import game.unit
import game.util


class Player(game.unit.Unit):
    def __init__(self, x, y, width, height, speed):
        super(Player, self).__init__(x, y, width, height, speed)

        self._alive = True

    def kill(self):
        self._alive = False

    def resurrect(self):
        self._alive = True

    def alive(self):
        return self._alive

    def move(self, direction, no_update=False):
        if self.alive():
            super().move(direction, no_update)

    def to_dict(self):
        result = super().to_dict()
        result.update({
            'alive': self._alive
        })
        return result

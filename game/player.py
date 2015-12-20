import game.unit
import game.util

RESURRECTION_TIME = 3


class Player(game.unit.Unit):
    TYPE = 'PLAYER'

    def __init__(self, x, y, width, height, speed):
        super(Player, self).__init__(x, y, width, height, speed)

        self._alive = True
        self._resurrection = 0

    def kill(self):
        self._alive = False
        self._resurrection = RESURRECTION_TIME
        self._need_update = True

    def resurrect(self):
        self._alive = True
        self._need_update = True

    def can_be_resurrected(self):
        return not self._alive and self._resurrection == 0

    def alive(self):
        return self._alive

    def move(self, direction, no_update=False):
        if self.alive():
            super().move(direction, no_update)

    def to_dict(self):
        result = super().to_dict()

        result.update({
            'alive': self._alive,
            'resurrection': {
                'left': self._resurrection / RESURRECTION_TIME,
                'speed': 1 / RESURRECTION_TIME
            }
        })
        return result

    def update(self, delta):
        super().update(delta)

        if self._resurrection > 0:
            self._resurrection = max(0, self._resurrection - delta)

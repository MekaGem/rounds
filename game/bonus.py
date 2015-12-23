import random

import game.unit


class Bonus(game.unit.Unit):
    TYPE = 'BONUS'
    LIFE_TIME = None
    EFFECT_TIME = None

    def __init__(self, room, x, y):
        super().__init__(room, x, y, 0.5, 0.5, 0)
        self._life_timer = self.LIFE_TIME
        self._timer = 0

    def update(self, delta):
        self._life_timer = max(0, self._life_timer - delta)
        self._timer = max(0, self._timer - delta)

    def alive(self):
        return self._life_timer > 0

    def activate(self):
        self._timer = self.EFFECT_TIME

    def active(self):
        return self._timer > 0

    def on_start(self, player):
        pass

    def on_stop(self, player):
        pass

    @classmethod
    def generate(cls, room):
        x = random.randint(0, room.width - 1) + 0.5
        y = random.randint(0, room.height - 1) + 0.5
        bonus = cls(room, x, y)
        return bonus


class SpeedBonus(Bonus):
    TYPE = 'SPEED_BONUS'
    LIFE_TIME = 4
    EFFECT_TIME = 3
    SPEED_BOOST = 1.5

    def on_start(self, player):
        player.speed *= self.SPEED_BOOST
        player.set_update()

    def on_stop(self, player):
        player.speed /= self.SPEED_BOOST
        player.set_update()

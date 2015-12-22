import game.unit
import game.util

RESURRECTION_TIME = 3


class Player(game.unit.Unit):
    TYPE = 'PLAYER'

    def __init__(self, x, y, width, height, speed):
        super(Player, self).__init__(x, y, width, height, speed)

        self._alive = True
        self._resurrection = 0
        self._ability = Invulnerability(self)

    def kill(self):
        self._alive = False
        self._resurrection = RESURRECTION_TIME
        self.set_update()

    def resurrect(self):
        self._alive = True
        self.set_update()

    def invulnerable(self):
        return isinstance(self._ability, Invulnerability) and self._ability.active()

    def use_ability(self):
        if self._ability.can_use():
            self._ability.use()

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
            },
            'invulnerable': self.invulnerable()
        })
        return result

    def update(self, delta):
        super().update(delta)
        self._resurrection = max(0, self._resurrection - delta)
        self._ability.update(delta)


class Invulnerability(object):
    COOLDOWN = 3
    DURATION = 1

    def __init__(self, player):
        self._cooldown = 0
        self._time_left = 0
        self._player = player

    def can_use(self):
        return self._player.alive() and self._cooldown == 0

    def active(self):
        return self._time_left > 0

    def update(self, delta):
        was_active = self.active()

        self._cooldown = max(0, self._cooldown - delta)
        self._time_left = max(0, self._time_left - delta)

        if was_active and not self.active():
            self._player.set_update()

    def use(self):
        self._cooldown = self.COOLDOWN
        self._time_left = self.DURATION
        self._player.set_update()

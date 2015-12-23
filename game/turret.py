import math
import random

import game.unit

ROTATION_SPEED = math.pi / 2
RELOAD_TIME = 0.4
PREPARE_TIME = 2
LIFE_TIME = 4


class Turret(game.unit.Unit):
    TYPE = 'TURRET'

    def __init__(self, room, x, y):
        super().__init__(room, x, y, 1, 1, 0)
        self._rotation = random.random() * math.pi * 2
        self._bullet_timer = RELOAD_TIME
        self._prepare_timer = PREPARE_TIME
        self._life_timer = LIFE_TIME

    def update(self, delta):
        super().update(delta)
        self._prepare_timer = max(0, self._prepare_timer - delta)
        if self._prepare_timer == 0:
            self._rotation += ROTATION_SPEED * delta
            if self._rotation >= math.pi * 2:
                self._rotation -= math.pi * 2

            self._bullet_timer = max(0, self._bullet_timer - delta)
            if self._bullet_timer == 0:
                self._shoot_bullet()
                self._bullet_timer = RELOAD_TIME

            self._life_timer = max(0, self._life_timer - delta)

    def _shoot_bullet(self):
        bullet = TurretBullet(self._room, self.x, self.y)
        bullet.move((math.cos(self._rotation), math.sin(self._rotation)))
        self._room.add_enemy(bullet)

    def to_dict(self):
        result = super().to_dict()
        result.update({
            'preparation': {
                'left': self._prepare_timer / PREPARE_TIME,
                'speed': 1 / PREPARE_TIME
            }
        })
        return result

    @classmethod
    def generate(cls, room):
        x = random.randint(0, room.width - 1) + 0.5
        y = random.randint(0, room.height - 1) + 0.5
        turret = cls(room, x, y)
        return turret

    def alive(self):
        return self._life_timer > 0

    def kills_player(self):
        return False

    def can_be_killed(self):
        return self._prepare_timer > 0


class TurretBullet(game.unit.Unit):
    TYPE = 'TURRET_BULLET'
    ghost = True
    simple_enemy = True

    def __init__(self, room, x, y):
        super().__init__(room, x, y, 0.2, 0.2, 6)

    def alive(self):
        return not self._room.out_of_bound(self.x, self.y)


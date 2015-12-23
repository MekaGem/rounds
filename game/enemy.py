import random

import game.unit
import game.util
import game.room


class Enemy(game.unit.Unit):
    TYPE = 'ENEMY'
    ghost = True

    def __init__(self, room, x, y):
        super().__init__(room, x, y, 1, 1, 6)

    @classmethod
    def generate(cls, room):
        side = random.randint(0, 3)
        if side == game.room.LEFT_SIDE:
            x = -game.room.STEP_OUT
            y = 0.5 + random.random() * (room.height - 1)
            direction = game.util.Direction(1, 0)
        elif side == game.room.RIGHT_SIDE:
            x = room.width + game.room.STEP_OUT
            y = 0.5 + random.random() * (room.height - 1)
            direction = game.util.Direction(-1, 0)
        elif side == game.room.DOWN_SIDE:
            x = 0.5 + random.random() * (room.width - 1)
            y = -game.room.STEP_OUT
            direction = game.util.Direction(0, 1)
        else:  # side == UP_SIDE
            x = 0.5 + random.random() * (room.width - 1)
            y = room.height + game.room.STEP_OUT
            direction = game.util.Direction(0, -1)

        enemy = cls(room, x, y)
        enemy.move(direction)
        return enemy

    def alive(self):
        return not self._room.out_of_bound(self.x, self.y)

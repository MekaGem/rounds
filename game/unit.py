import math

import game.util


class Unit(object):
    id = 0

    def __init__(self, x, y, width, height, speed):
        self.id = Unit.id
        Unit.id += 1

        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = speed
        self.direction = None

        self._need_update = False

        self._room = None

    def set_room(self, room):
        self._room = room

    def to_dict(self):
        return {
            'id': self.id,
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'moving': {
                'x_speed': self.direction.x * self.speed,
                'y_speed': self.direction.y * self.speed
            } if self.direction else {
                'x_speed': 0,
                'y_speed': 0
            }
        }

    def need_update(self):
        return self._need_update

    def updated(self):
        self._need_update = False

    def move(self, direction):
        changed = False
        if direction is None:
            changed = bool(self.direction)

            self.direction = None
        else:
            if self.x <= 0.5 and direction[0] == -1:
                direction[0] = 0
            if self.x >= self._room.width - 0.5 and direction[0] == 1:
                direction[0] = 0

            if self.y <= 0.5 and direction[1] == -1:
                direction[1] = 0
            if self.y >= self._room.height - 0.5 and direction[1] == 1:
                direction[1] = 0

            if abs(direction[0]) == 1 and abs(direction[1]) == 1:
                sq = math.sqrt(2)
                direction[0] /= sq
                direction[1] /= sq

            if not self.direction or (self.direction.x != direction[0] or self.direction.y != direction[1]):
                changed = True

            self.direction = game.util.Direction(
                direction[0],
                direction[1]
            )

        if changed:
            self._need_update = True

    def _inside_x(self, x):
        return 0.5 < x < self._room.width - 0.5

    def _inside_y(self, y):
        return 0.5 < y < self._room.height - 0.5

    def update(self, delta):
        if self.direction:
            old_x = self.x
            old_y = self.y

            self.x += self.direction.x * self.speed * delta
            self.y += self.direction.y * self.speed * delta

            if self._inside_x(old_x) and not self._inside_x(self.x):
                self.x = max(0.5, min(self._room.width - 0.5, self.x))
                self._need_update = True
                self.direction = game.util.Direction(0, self.direction.y)

            if self._inside_y(old_y) and not self._inside_y(self.y):
                self.y = max(0.5, min(self._room.height - 0.5, self.y))
                self._need_update = True
                self.direction = game.util.Direction(self.direction.x, 0)

import random
import itertools

import game.message
import game.enemy
import game.util

LEFT_SIDE = 0
UP_SIDE = 1
RIGHT_SIDE = 2
DOWN_SIDE = 3

STEP_OUT = 2


class Room(object):
    def __init__(self, width, height, handler):
        self.width = width
        self.height = height
        self._passable = [[True] * height] * width
        self._players = {}
        self._enemies = {}
        self._handler = handler

        self._enemies_to_create = 0
        self._enemies_to_die = 0
        self._enemy_timer = 0
        self._round_pause = 0

        self._round_step = 0.2

    def add_player(self, player):
        self._players[player.id] = player
        player.set_room(self)

    def remove_player(self, player_id):
        del self._players[player_id]

    def get_player(self, player_id):
        return self._players[player_id]

    def players(self):
        return self._players.values()

    def update(self, delta):
        for unit in itertools.chain(self._players.values(), self._enemies.values()):
            unit.update(delta)

        if self._check_new_round():
            if self._round_pause is None:
                self._round_pause = 5
            else:
                self._round_pause = max(0, self._round_pause - delta)
                if self._round_pause == 0:
                    self._new_round()
                    self._handler.announce_to_room(self, game.message.round_started())
                    self._round_pause = None
                    self._enemy_timer += 1
        else:
            self._enemy_timer = max(0, self._enemy_timer - delta)
            if self._enemy_timer == 0 and self._enemies_to_create > 0:
                self._create_enemy()
                self._enemy_timer += random.random() * (0.5 + self._round_step) + self._round_step
            self._kill_enemies()
            self._check_intersections()

    def _check_new_round(self):
        return self._enemies_to_die == 0

    def _new_round(self):
        self._enemies_to_create = self._enemies_to_die = 50

        for player in [player for player in self._players.values() if not player.alive()]:
            player.resurrect()
            self._handler.announce_to_room(self, game.message.player_update(player))

        self._round_step *= 0.9

    def _create_enemy(self):
        side = random.randint(0, 3)
        if side == LEFT_SIDE:
            x = -STEP_OUT
            y = 0.5 + random.random() * (self.height - 1)
            direction = game.util.Direction(1, 0)
        elif side == RIGHT_SIDE:
            x = self.width + STEP_OUT
            y = 0.5 + random.random() * (self.height - 1)
            direction = game.util.Direction(-1, 0)
        elif side == DOWN_SIDE:
            x = 0.5 + random.random() * (self.width - 1)
            y = -STEP_OUT
            direction = game.util.Direction(0, 1)
        else:  # side == UP_SIDE
            x = 0.5 + random.random() * (self.width - 1)
            y = self.height + STEP_OUT
            direction = game.util.Direction(0, -1)

        enemy = game.enemy.Enemy(x, y)
        enemy.set_room(self)
        enemy.move(direction)

        self._handler.announce_to_room(self, game.message.enemy_update(enemy))

        self._enemies[enemy.id] = enemy
        self._enemies_to_create -= 1

    def _kill_enemies(self):
        def _out_of_bound(width, height, x, y):
            return x < -STEP_OUT or x > width + STEP_OUT or y < -STEP_OUT or y > height + STEP_OUT

        for enemy_id, enemy in list(self._enemies.items()):
            if _out_of_bound(self.width, self.height, enemy.x, enemy.y):
                del self._enemies[enemy_id]
                self._enemies_to_die -= 1
                self._handler.announce_to_room(self, game.message.enemy_removed(enemy))

    def _check_intersections(self):
        for player in [player for player in self._players.values() if player.alive()]:
            for enemy in self._enemies.values():
                if player.intersects(enemy):
                    player.move([0, 0], no_update=True)
                    player.kill()
                    self._handler.announce_to_room(self, game.message.player_update(player))
                    break



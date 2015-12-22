import random
import itertools

import game.message
import game.enemy
import game.turret
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
        self._enemy_timer = 0
        self._round_pause = 0
        self._current_round = 0
        self._round_step = 0.4

    def add_player(self, player):
        self._players[player.id] = player
        player.set_room(self)

    def remove_player(self, player_id):
        del self._players[player_id]

    def get_player(self, player_id):
        return self._players[player_id]

    def players(self):
        return self._players.values()

    def add_enemy(self, enemy):
        self._enemies[enemy.id] = enemy
        self._handler.announce_to_room(self, game.message.unit_update(enemy))

    def update(self, delta):
        for unit in list(itertools.chain(self._players.values(), self._enemies.values())):
            unit.update(delta)

        self._kill_enemies()
        self._check_intersections()

        if self._check_new_round():
            if self._round_pause is None:
                self._round_pause = 3
            else:
                self._round_pause = max(0, self._round_pause - delta)
                if self._round_pause == 0:
                    self._new_round()
                    self._handler.announce_to_room(self, game.message.round_started(self._current_round))
                    self._round_pause = None
                    self._enemy_timer += 1
        else:
            self._enemy_timer = max(0, self._enemy_timer - delta)
            if self._enemy_timer == 0 and self._enemies_to_create > 0:
                self._create_enemy()
                self._enemy_timer += random.random() * (0.5 + self._round_step) + self._round_step

    def out_of_bound(self, x, y):
        return x < -STEP_OUT or x > self.width + STEP_OUT or y < -STEP_OUT or y > self.height + STEP_OUT

    def _check_new_round(self):
        return self._enemies_to_create == 0 and not self._enemies

    def _new_round(self):
        self._current_round += 1
        self._enemies_to_create = 50

        for player in [player for player in self._players.values() if not player.alive()]:
            player.resurrect()

        self._round_step *= 0.9

    def _create_enemy(self):
        if random.random() < 0.9:
            enemy = game.enemy.Enemy.generate(self)
        else:
            enemy = game.turret.Turret.generate(self)

        self._handler.announce_to_room(self, game.message.unit_update(enemy))

        self._enemies[enemy.id] = enemy
        self._enemies_to_create -= 1

    def _kill_enemies(self):
        for enemy_id, enemy in list(self._enemies.items()):
            if not enemy.alive():
                del self._enemies[enemy_id]
                self._handler.announce_to_room(self, game.message.unit_removed(enemy))

    def _check_intersections(self):
        for player in [player for player in self._players.values() if player.alive()]:
            for enemy in self._enemies.values():
                if enemy.kills_player() and player.intersects(enemy) and not player.invulnerable():
                    player.move([0, 0])
                    player.kill()
                    break

            for friend in self._players.values():
                if player.intersects(friend) and friend.can_be_resurrected():
                    friend.resurrect()

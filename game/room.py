import random
import itertools

import game.bonus
import game.message
import game.enemy
import game.turret
import game.util

LEFT_SIDE = 0
UP_SIDE = 1
RIGHT_SIDE = 2
DOWN_SIDE = 3

STEP_OUT = 2

BONUS_TIME = 5


class Room(object):
    def __init__(self, width, height, handler):
        self.width = width
        self.height = height
        self._passable = [[True] * height] * width
        self._players = {}
        self._enemies = {}
        self._bonuses = {}
        self._handler = handler

        self._enemies_to_create = 0
        self._enemy_timer = 0

        self._bonuses_to_create = 0
        self._bonus_timer = BONUS_TIME

        self._round_pause = 0
        self._current_round = 0
        self._round_step = 0.4

    def add_player(self, player):
        self._players[player.id] = player

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
        everybody = list(itertools.chain(
            self._players.values(),
            self._enemies.values(),
            self._bonuses.values()
        ))
        for unit in everybody:
            unit.update(delta)

        self._kill_enemies()
        self._kill_bonuses()
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
                self._enemy_timer = random.random() * (0.5 + self._round_step) + self._round_step

            self._bonus_timer = max(0, self._bonus_timer - delta)
            if self._bonus_timer == 0 and self._bonuses_to_create > 0:
                self._create_bonus()
                self._bonus_timer = BONUS_TIME

    def out_of_bound(self, x, y):
        return x < -STEP_OUT or x > self.width + STEP_OUT or y < -STEP_OUT or y > self.height + STEP_OUT

    def _check_new_round(self):
        return self._enemies_to_create == 0 and not self._enemies

    def _new_round(self):
        self._current_round += 1
        self._enemies_to_create = 50
        self._bonuses_to_create = 6

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

    def _create_bonus(self):
        bonus = game.bonus.SpeedBonus.generate(self)

        self._handler.announce_to_room(self, game.message.unit_update(bonus))
        self._bonuses[bonus.id] = bonus
        pass

    def _kill_enemy(self, enemy):
        del self._enemies[enemy.id]
        self._handler.announce_to_room(self, game.message.unit_removed(enemy))

    def _kill_enemies(self):
        for enemy in list(self._enemies.values()):
            if not enemy.alive():
                self._kill_enemy(enemy)

    def _kill_bonus(self, bonus):
        del self._bonuses[bonus.id]
        self._handler.announce_to_room(self, game.message.unit_removed(bonus))

    def _kill_bonuses(self):
        for bonus in list(self._bonuses.values()):
            if not bonus.alive():
                self._kill_bonus(bonus)

    def _check_intersections(self):
        dead_players = set()

        for player in [player for player in self._players.values() if player.alive()]:
            for enemy in [enemy for enemy in self._enemies.values() if enemy.intersects(player)]:
                if enemy.kills_player() and not player.invulnerable():
                    dead_players.add(player)

                if enemy.can_be_killed() and player.alive():
                    self._kill_enemy(enemy)

            for bonus in [bonus for bonus in self._bonuses.values() if bonus.intersects(player)]:
                if bonus.alive() and player.alive():
                    self._kill_bonus(bonus)
                    player.give_bonus(bonus)
                    bonus.activate()

            for friend in self._players.values():
                if player.intersects(friend) and friend.can_be_resurrected():
                    friend.resurrect()

        for player in dead_players:
            player.move([0, 0])
            player.kill()

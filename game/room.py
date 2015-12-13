import game.message


class Room(object):
    def __init__(self, width, height, handler):
        self.width = width
        self.height = height
        self._passable = [[True] * height] * width
        self._players = {}
        self._handler = handler

        self._round_time = 5

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
        for player_id, player in self._players.items():
            player.update(delta)

        self._round_time = max(0, self._round_time - delta)
        if self._round_time == 0:
            self._handler.announce_to_room(self, game.message.round_started())
            self._round_time = 5

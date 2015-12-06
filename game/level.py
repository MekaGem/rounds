class Level(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self._passable = [[True] * height] * width
        self._players = {}

    def add_player(self, player):
        self._players[player.id] = player
        player.set_level(self)

    def remove_player(self, player_id):
        del self._players[player_id]

    def get_player(self, player_id):
        return self._players[player_id]

    def players(self):
        return self._players.values()

    def update(self, delta):
        for player_id, player in self._players.items():
            player.update(delta)

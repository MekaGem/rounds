import game.unit


class Enemy(game.unit.Unit):
    def __init__(self, x, y):
        super().__init__(x, y, 1, 1, 6)

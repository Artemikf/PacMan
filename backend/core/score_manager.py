


DOT_POINTS = 10
ENERGIZER_POINTS = 50
GHOST_BASE_POINTS = 200  # doubles each consecutive ghost eaten

class ScoreManager:
    STARTING_LIVES = 3

    def __init__(self):
        self.score = 0
        self.lives = self.STARTING_LIVES
        self._ghost_combo = 0


    # рестарт игры
    def reset(self) -> None:
        self.score = 0
        self.lives = self.STARTING_LIVES
        self._ghost_combo = 0
import json
from pathlib import Path

HIGH_SCORE_FILE = Path("high_score.json")

DOT_POINTS = 10
ENERGIZER_POINTS = 50
GHOST_BASE_POINTS = 200  # doubles each consecutive ghost eaten

class ScoreManager:
    STARTING_LIVES = 3

    def __init__(self):
        self.score = 0
        self.lives = self.STARTING_LIVES
        self._ghost_combo = 0
        self.high_score = self._load_high_score()

    # ─────────── очки
    def add_points(self, pts: int) -> None:
        self.score += pts
        if self.score > self.high_score:
            self.high_score = self.score
            self._save_high_score()

    def add_dot(self) -> None:
        self.add_points(DOT_POINTS)

    def reset_combo(self) -> None:
        self._ghost_combo = 0

    def add_energizer(self) -> None:
        self.add_points(ENERGIZER_POINTS)
        self._ghost_combo = 0

    def add_ghost_eaten(self) -> int:
        self._ghost_combo += 1
        pts = GHOST_BASE_POINTS * (2 ** (self._ghost_combo - 1))
        self.add_points(pts)
        return pts

    # ─────────── рестарт игры
    def reset(self) -> None:
        self.score = 0
        self.lives = self.STARTING_LIVES
        self._ghost_combo = 0

    def lose_life(self) -> None:
        if self.lives > 0:
            self.lives -= 1
        self._ghost_combo = 0

    # ─────────── сейв / лоад
    def _save_high_score(self) -> None:
        try:
            HIGH_SCORE_FILE.write_text(json.dumps({"high_score": self.high_score}))
        except OSError:
            pass

    def _load_high_score(self) -> int:
        try:
            if HIGH_SCORE_FILE.exists():
                data = json.loads(HIGH_SCORE_FILE.read_text())
                return int(data.get("high_score", 0))
        except (json.JSONDecodeError, ValueError):
            pass
        return 0
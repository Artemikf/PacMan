from enum import Enum, auto
from typing import Optional
from backend.core.game_map import GameMap
from backend.entities.pacman import PacMan
from backend.entities.ghost import Ghost, GhostPersonality
from backend.core.score_manager import ScoreManager
from backend.utils.config import GameConfig

# перечисление состояний
class GameState(Enum):
    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    VICTORY = auto()

# центральный игровой движок
class GameEngine:

    def __init__(self, config: GameConfig):
        self.config = config
        self.state = GameState.MENU
        self.level = 1
        self.score_manager = ScoreManager()
        self.game_map: Optional[GameMap] = None
        self.pacman: Optional[PacMan] = None
        self.ghosts: list[Ghost] = []
        self._running = False


    # ─────────────────────── режими
    def start_game(self) -> None:
        self._setup_level(self.level)
        self.state = GameState.PLAYING
        self._running = True

    def pause(self) -> None:
        if self.state == GameState.PLAYING:
            self.state = GameState.PAUSED

    def resume(self) -> None:
        if self.state == GameState.PAUSED:
            self.state = GameState.PLAYING

    def restart(self) -> None:
        self.level = 1
        self.score_manager.reset()
        self.start_game()

    # ── Цикл обновления

    def update(self, dt: float) -> None:
        if self.state != GameState.PLAYING:
            return
        self.pacman.update(dt, self.game_map)
        for ghost in self.ghosts:
            ghost.update(dt, self.game_map, self.pacman.position)
        self._check_collisions()
        self._check_game_state()

    # ── Обнаружение столкновений

    def _check_collisions(self) -> None:
        self._check_dot_collision()
        self._check_energizer_collision()
        self._check_ghost_collision()
        self._check_fruit_collision()

    def _check_dot_collision(self) -> None:
        pos = self.pacman.grid_position
        if self.game_map.consume_dot(pos):
            self.score_manager.add_dot()

    def _check_energizer_collision(self) -> None:
        pos = self.pacman.grid_position
        if self.game_map.consume_energizer(pos):
            self.score_manager.add_energizer()
            for ghost in self.ghosts:
                ghost.frighten(self.config.frighten_duration)

    def _check_ghost_collision(self) -> None:
        for ghost in self.ghosts:
            if ghost.collides_with(self.pacman.position):
                if ghost.is_frightened:
                    ghost.die()
                    pts = self.score_manager.add_ghost_eaten()
                    ghost.eaten_score = pts
                else:
                    self._pacman_dies()
                    return

    def _check_fruit_collision(self) -> None:
        if self.game_map.fruit and self.game_map.fruit.collides_with(self.pacman.position):
            pts = self.game_map.fruit.collect()
            self.score_manager.add_points(pts)

    # ── Государственные проверки

    def _check_game_state(self) -> None:
        if self.game_map.all_dots_eaten():
            if self.level < self.config.max_levels:
                self.level += 1
                self._setup_level(self.level)
            else:
                self.state = GameState.VICTORY

    def _pacman_dies(self) -> None:
        if self.score_manager.lives > 1:
            self.score_manager.lose_life()
            self._reset_positions()
        else:
            self.score_manager.lose_life()
            self.state = GameState.GAME_OVER

    # ── Помощники по настройке

    def _setup_level(self, level: int) -> None:
        self.game_map = GameMap(level)
        self.pacman = PacMan(self.game_map.pacman_start, self.config)
        self.ghosts = self._create_ghosts(level)
        self.score_manager.reset_combo()

    def _reset_positions(self) -> None:
        self.pacman.reset(self.game_map.pacman_start)
        for ghost in self.ghosts:
            ghost.reset()

    def _create_ghosts(self, level: int) -> list[Ghost]:
        speed_mult = 1.0 + (level - 1) * self.config.ghost_speed_increase
        starts = self.game_map.ghost_starts
        personalities = [
            GhostPersonality.CHASER,
            GhostPersonality.AMBUSHER,
            GhostPersonality.FICKLE,
            GhostPersonality.COWARD,
        ]
        return [
            Ghost(starts[i % len(starts)], personalities[i], speed_mult, self.config)
            for i in range(self.config.ghost_count)
        ]

    # ── Общедоступные методы доступа

    @property
    def score(self) -> int:
        return self.score_manager.score

    @property
    def lives(self) -> int:
        return self.score_manager.lives

    @property
    def high_score(self) -> int:
        return self.score_manager.high_score



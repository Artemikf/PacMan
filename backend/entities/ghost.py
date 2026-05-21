
from __future__ import annotations
import random
import math
from enum import Enum, auto
from backend.core.game_map import Vec2, GameMap
from backend.utils.config import GameConfig

TILE = 32  # пикселей — локальный псевдоним

class GhostPersonality(Enum):
    CHASER   = auto()   # Blinky — всегда нацеливается непосредственно на Пакмана
    AMBUSHER = auto()   # Pinky   — нацеливается на 4 клетки впереди Пакмана
    FICKLE   = auto()   # Inky    — случайные смещения
    COWARD   = auto()   # Clyde   — убегает, когда к нему подходят


class GhostMode(Enum):
    CHASE    = auto()
    SCATTER  = auto()
    FRIGHTENED = auto()
    EATEN    = auto()


# Расставить угловые мишени (строка, столбец)
SCATTER_TARGETS = {
    GhostPersonality.CHASER:   (0, 18),
    GhostPersonality.AMBUSHER: (0, 2),
    GhostPersonality.FICKLE:   (21, 18),
    GhostPersonality.COWARD:   (21, 2),
}

GHOST_COLORS = {
    GhostPersonality.CHASER:   (255, 0,   0),    # red
    GhostPersonality.AMBUSHER: (255, 184, 255),  # pink
    GhostPersonality.FICKLE:   (0,   255, 255),  # cyan
    GhostPersonality.COWARD:   (255, 184, 82),   # orange
}


class Ghost:
    COLLISION_RADIUS = 12
    EATEN_SPEED_MULT = 2.0
    FRIGHTENED_SPEED_MULT = 0.5
    HOME_ROW, HOME_COL = 9, 9  # ghost house centre

    def __init__(
        self,
        start: Vec2,
        personality: GhostPersonality,
        speed_mult: float,
        config: GameConfig,
    ):
        self.personality = personality
        self.color = GHOST_COLORS[personality]
        self._start = Vec2(start.x, start.y)
        self.position = Vec2(start.x, start.y)
        self.base_speed = config.ghost_speed * speed_mult
        self.mode = GhostMode.SCATTER
        self._frighten_timer: float = 0.0
        self._scatter_timer: float = 7.0
        self._chase_timer: float = 0.0
        self._phase_time: float = 0.0
        self.eaten_score: int = 0
        self._dir = Vec2(0, -1)  # начальное направление: вверх

    # ── Public API

    @property
    def is_frightened(self) -> bool:
        return self.mode == GhostMode.FRIGHTENED

    @property
    def is_eaten(self) -> bool:
        return self.mode == GhostMode.EATEN

    def frighten(self, duration: float) -> None:
        if self.mode not in (GhostMode.EATEN,):
            self.mode = GhostMode.FRIGHTENED
            self._frighten_timer = duration

    def die(self) -> None:
        self.mode = GhostMode.EATEN

    def reset(self) -> None:
        self.position = Vec2(self._start.x, self._start.y)
        self.mode = GhostMode.SCATTER
        self._frighten_timer = 0.0
        self._phase_time = 0.0

    def collides_with(self, pos: Vec2) -> bool:
        return pos.distance_to(self.position) < self.COLLISION_RADIUS

    # ── Update

    def update(self, dt: float, game_map: GameMap, pacman_pos: Vec2) -> None:
        self._update_mode(dt)
        target = self._compute_target(pacman_pos, game_map)
        speed = self._effective_speed()
        self._move_toward(target, speed, dt, game_map)

    # ── Mode transitions

    def _update_mode(self, dt: float) -> None:
        if self.mode == GhostMode.FRIGHTENED:
            self._frighten_timer -= dt
            if self._frighten_timer <= 0:
                self.mode = GhostMode.SCATTER
                self._phase_time = 0.0
        elif self.mode == GhostMode.EATEN:
            pass  # обрабатывается по возвращении в начальную точку
        else:
            self._phase_time += dt
            if self.mode == GhostMode.SCATTER and self._phase_time > 7.0:
                self.mode = GhostMode.CHASE
                self._phase_time = 0.0
            elif self.mode == GhostMode.CHASE and self._phase_time > 20.0:
                self.mode = GhostMode.SCATTER
                self._phase_time = 0.0

    # ── Target selection

    def _compute_target(self, pacman_pos: Vec2, game_map: GameMap) -> Vec2:
        if self.mode == GhostMode.FRIGHTENED:
            # Случайная допустимая плитка
            row = random.randint(0, game_map.rows - 1)
            col = random.randint(0, game_map.cols - 1)
            return Vec2.from_grid(row, col, TILE)

        if self.mode == GhostMode.EATEN:
            return Vec2.from_grid(self.HOME_ROW, self.HOME_COL, TILE)

        if self.mode == GhostMode.SCATTER:
            r, c = SCATTER_TARGETS[self.personality]
            return Vec2.from_grid(r, c, TILE)

        # CHASE mode
        return self._chase_target(pacman_pos)

    def _chase_target(self, pacman_pos: Vec2) -> Vec2:
        if self.personality == GhostPersonality.CHASER:
            return pacman_pos

        if self.personality == GhostPersonality.AMBUSHER:
            return Vec2(pacman_pos.x + 4 * TILE, pacman_pos.y)

        if self.personality == GhostPersonality.FICKLE:
            offset = random.choice([-2, -1, 0, 1, 2])
            return Vec2(pacman_pos.x + offset * TILE, pacman_pos.y + offset * TILE)

        # COWARD: если он близко — беги; в противном случае — преследуй
        if self.position.distance_to(pacman_pos) < 8 * TILE:
            return Vec2(
                self.position.x + (self.position.x - pacman_pos.x),
                self.position.y + (self.position.y - pacman_pos.y),
            )
        return pacman_pos

    # ── Movement

    def _effective_speed(self) -> float:
        if self.mode == GhostMode.FRIGHTENED:
            return self.base_speed * self.FRIGHTENED_SPEED_MULT
        if self.mode == GhostMode.EATEN:
            return self.base_speed * self.EATEN_SPEED_MULT
        return self.base_speed

    def _move_toward(self, target: Vec2, speed: float, dt: float, game_map: GameMap) -> None:
        # Движение по сетке: выбирайте оптимальный поворот на каждом перекрестке
        step = speed * dt
        # Центр текущей плитки
        ts = TILE
        col = int(self.position.x // ts)
        row = int(self.position.y // ts)
        centre_x = col * ts + ts // 2
        centre_y = row * ts + ts // 2

        # Мы находимся рядом с центром плитки? (пороговое значение = 4 пикселя)
        near_centre = (
            abs(self.position.x - centre_x) < 4 and
            abs(self.position.y - centre_y) < 4
        )

        if near_centre:
            best_dir = self._best_direction(row, col, target, game_map)
            if best_dir:
                self._dir = best_dir

        # Выровнять по центру, затем переместить
        if near_centre:
            self.position.x = float(centre_x)
            self.position.y = float(centre_y)

        new_x = self.position.x + self._dir.x * step
        new_y = self.position.y + self._dir.y * step
        nr = int(new_y // ts)
        nc = int(new_x // ts)
        if not game_map.is_wall(nr, nc):
            self.position.x = new_x
            self.position.y = new_y

        # Облицовка туннеля
        w = game_map.pixel_width()
        if self.position.x < 0:
            self.position.x = float(w - 1)
        elif self.position.x >= w:
            self.position.x = 0.0

        # Воскресить, если съеденный призрак добрался до дома
        if self.mode == GhostMode.EATEN:
            if self.position.distance_to(Vec2.from_grid(self.HOME_ROW, self.HOME_COL, ts)) < 4:
                self.mode = GhostMode.SCATTER
                self._phase_time = 0.0

    def _best_direction(self, row: int, col: int, target: Vec2, game_map: GameMap) -> Vec2 | None:
        candidates = [Vec2(0,-1), Vec2(0,1), Vec2(-1,0), Vec2(1,0)]
        # Не двигаться задним ходом
        reverse = Vec2(-self._dir.x, -self._dir.y)
        options = []
        for d in candidates:
            if d.x == reverse.x and d.y == reverse.y:
                continue
            nr = row + int(d.y)
            nc = col + int(d.x)
            if not game_map.is_wall(nr, nc):
                tx = nc * TILE + TILE // 2
                ty = nr * TILE + TILE // 2
                dist = math.hypot(tx - target.x, ty - target.y)
                options.append((dist, d))
        if not options:
            return reverse  # forced reverse
        options.sort(key=lambda x: x[0])
        return options[0][1]











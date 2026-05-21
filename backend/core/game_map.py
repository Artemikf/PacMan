from dataclasses import dataclass
import copy
from typing import Optional

# ─────────────── главные константы
WALL = 0
DOT = 1
ENERGIZER = 2
EMPTY = 3
GHOST_HOUSE = 4
FRUIT_SPAWN = 5


# ──── Классический шаблон лабиринта 21×21 (0=стена, 1=точка, 2=генератор, 3=пустой, 4=дом привидений)
BASE_MAZE = [
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,0],
    [0,2,0,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,2,0],
    [0,1,0,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,1,0],
    [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
    [0,1,0,0,1,0,1,0,0,0,0,0,0,0,1,0,1,0,0,1,0],
    [0,1,1,1,1,0,1,1,1,0,0,0,1,1,1,0,1,1,1,1,0],
    [0,0,0,0,1,0,0,0,3,0,0,0,3,0,0,0,1,0,0,0,0],
    [0,0,0,0,1,0,3,3,3,3,3,3,3,3,3,0,1,0,0,0,0],
    [0,0,0,0,1,0,3,0,4,4,4,4,4,0,3,0,1,0,0,0,0],
    [3,3,3,3,1,3,3,0,4,4,4,4,4,0,3,3,1,3,3,3,3],
    [0,0,0,0,1,0,3,0,0,0,0,0,0,0,3,0,1,0,0,0,0],
    [0,0,0,0,1,0,3,3,3,3,5,3,3,3,3,0,1,0,0,0,0],
    [0,0,0,0,1,0,3,0,0,0,0,0,0,0,3,0,1,0,0,0,0],
    [0,1,1,1,1,1,1,1,1,0,0,0,1,1,1,1,1,1,1,1,0],
    [0,1,0,0,1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,1,0],
    [0,2,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,2,0],
    [0,0,1,0,1,0,1,0,0,0,0,0,0,0,1,0,1,0,1,0,0],
    [0,1,1,1,1,0,1,1,1,0,0,0,1,1,1,0,1,1,1,1,0],
    [0,1,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,1,0],
    [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
]

ROWS = len(BASE_MAZE)
COLS = len(BASE_MAZE[0])

@dataclass
class Vec2:
    x: float
    y: float

    def __add__(self, other: "Vec2") -> "Vec2":
        return Vec2(self.x + other.x, self.y + other.y)

    def distance_to(self, other: "Vec2") -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

    def to_grid(self, tile_size: int) -> tuple[int, int]:
        return (int(self.y // tile_size), int(self.x // tile_size))

    @staticmethod
    def from_grid(row: int, col: int, tile_size: int) -> "Vec2":
        return Vec2(col * tile_size + tile_size // 2, row * tile_size + tile_size // 2)

@dataclass
class Fruit:
    position: Vec2
    points: int = 100
    active: bool = True
    timer: float = 10.0  # seconds visible

    def update(self, dt: float) -> None:
        if self.active:
            self.timer -= dt
            if self.timer <= 0:
                self.active = False

    def collides_with(self, pos: Vec2, radius: float = 12.0) -> bool:
        return self.active and pos.distance_to(self.position) < radius

    def collect(self) -> int:
        self.active = False
        return self.points


class GameMap:
    # Управляет сеткой плиток, точками, активаторами и появлением фруктов

    TILE_SIZE = 32

    def __init__(self, level: int = 1):
        self.level = level
        self.grid: list[list[int]] = copy.deepcopy(BASE_MAZE)
        self.rows = ROWS
        self.cols = COLS
        self.total_dots = self._count_collectibles()
        self.eaten_dots = 0
        self.fruit: Optional[Fruit] = None
        self._fruit_spawned = False
        self._fruit_threshold = self.total_dots // 2

    # ───────── аксессуары

    @property
    def pacman_start(self) -> Vec2:
        return Vec2.from_grid(16, 10, self.TILE_SIZE)

    @property
    def ghost_starts(self) -> list[Vec2]:
        return [
            Vec2.from_grid(9, 8, self.TILE_SIZE),
            Vec2.from_grid(9, 9, self.TILE_SIZE),
            Vec2.from_grid(9, 10, self.TILE_SIZE),
            Vec2.from_grid(9, 11, self.TILE_SIZE),
        ]

    def is_wall(self, row: int, col: int) -> bool:
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return True
        return self.grid[row][col] == WALL

    def tile_at(self, row: int, col: int) -> int:
        if not (0 <= row < self.rows and 0 <= col < self.cols):
            return WALL
        return self.grid[row][col]

    # ── Consumables

    def consume_dot(self, pos: Vec2) -> bool:
        row, col = pos.to_grid(self.TILE_SIZE)
        if self.grid[row][col] == DOT:
            self.grid[row][col] = EMPTY
            self.eaten_dots += 1
            self._maybe_spawn_fruit()
            return True
        return False

    def consume_energizer(self, pos: Vec2) -> bool:
        row, col = pos.to_grid(self.TILE_SIZE)
        if self.grid[row][col] == ENERGIZER:
            self.grid[row][col] = EMPTY
            self.eaten_dots += 1
            return True
        return False

    def all_dots_eaten(self) -> bool:
        return self.eaten_dots >= self.total_dots

    def update(self, dt: float) -> None:
        if self.fruit:
            self.fruit.update(dt)
            if not self.fruit.active:
                self.fruit = None

    # ── Fruit

    def _maybe_spawn_fruit(self) -> None:
        if not self._fruit_spawned and self.eaten_dots >= self._fruit_threshold:
            self._fruit_spawned = True
            fruit_pts = 100 + (self.level - 1) * 50
            self.fruit = Fruit(Vec2.from_grid(12, 10, self.TILE_SIZE), fruit_pts)

    # ── Helpers

    def _count_collectibles(self) -> int:
        count = 0
        for row in self.grid:
            for cell in row:
                if cell in (DOT, ENERGIZER):
                    count += 1
        return count

    def pixel_width(self) -> int:
        return self.cols * self.TILE_SIZE

    def pixel_height(self) -> int:
        return self.rows * self.TILE_SIZE














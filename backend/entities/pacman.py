from backend.core.game_map import Vec2, GameMap
from backend.utils.config import GameConfig

# кардинальные направления (dx, dy) в пикселях
DIR_RIGHT = Vec2(1, 0)
DIR_LEFT  = Vec2(-1, 0)
DIR_UP    = Vec2(0, -1)
DIR_DOWN  = Vec2(0, 1)
STOPPED   = Vec2(0, 0)


class PacMan:

    MOUTH_OPEN_ANGLE   = 45   # степени
    MOUTH_ANIM_SPEED   = 8    # полных циклов открытия-закрытия в секунду
    COLLISION_RADIUS   = 10

    def __init__(self, start: Vec2, config: GameConfig):
        self.position = Vec2(start.x, start.y)
        self._start = Vec2(start.x, start.y)
        self.config = config
        self.direction = DIR_RIGHT
        self._queued_dir = DIR_RIGHT
        self.speed = config.pacman_speed
        # Animation
        self.mouth_angle: float = 45.0  # 0 = closed, 45 = fully open
        self._anim_opening = True
        self._anim_time: float = 0.0
        self.alive = True

    # ── Public API

    def set_direction(self, direction: Vec2) -> None:
        # Запросить изменение направления; применяется, когда ход легален
        self._queued_dir = direction

    def update(self, dt: float, game_map: GameMap) -> None:
        if not self.alive:
            return
        self._try_turn(game_map)
        self._move(dt, game_map)
        self._animate_mouth(dt)

    def reset(self, start: Vec2) -> None:
        self.position = Vec2(start.x, start.y)
        self.direction = DIR_RIGHT
        self._queued_dir = DIR_RIGHT
        self.alive = True
        self.mouth_angle = 45.0

    @property
    def grid_position(self) -> Vec2:
        return self.position

    # ──  helpers

    def _try_turn(self, game_map: GameMap) -> None:
        if self._queued_dir == self.direction:
            return
        if self._can_move_in(self._queued_dir, game_map):
            self.direction = self._queued_dir

    def _move(self, dt: float, game_map: GameMap) -> None:
        if self.direction == STOPPED:
            return
        step = self.speed * dt
        new_x = self.position.x + self.direction.x * step
        new_y = self.position.y + self.direction.y * step
        ts = game_map.TILE_SIZE
        row = int(new_y // ts)
        col = int(new_x // ts)
        if not game_map.is_wall(row, col):
            self.position.x = new_x
            self.position.y = new_y
        # Обертка туннеля (левый/правый края)
        w = game_map.pixel_width()
        if self.position.x < 0:
            self.position.x = w - 1
        elif self.position.x >= w:
            self.position.x = 0

    def _can_move_in(self, direction: Vec2, game_map: GameMap) -> bool:
        ts = game_map.TILE_SIZE
        test_x = self.position.x + direction.x * ts * 0.5
        test_y = self.position.y + direction.y * ts * 0.5
        row = int(test_y // ts)
        col = int(test_x // ts)
        return not game_map.is_wall(row, col)

    def _animate_mouth(self, dt: float) -> None:
        self._anim_time += dt
        # Колебание между 0 и MOUTH_OPEN_ANGLE
        half = 1.0 / (2 * self.MOUTH_ANIM_SPEED) # при speed=8: half = 0.0625s
        phase = self._anim_time % (2 * half) # фаза от 0 до 0.125
        if phase < half:
            self.mouth_angle = self.MOUTH_OPEN_ANGLE * (phase / half) # 0→45
        else:
            self.mouth_angle = self.MOUTH_OPEN_ANGLE * (1 - (phase - half) / half) # 45→0

    # ── Угол поворота для рендерера

    @property
    def rotation_deg(self) -> float:
        # Возвращает градусы для поворота спрайта так, чтобы он смотрел в направлении движения
        if self.direction == DIR_RIGHT: return 0
        if self.direction == DIR_LEFT:  return 180
        if self.direction == DIR_UP:    return 90
        if self.direction == DIR_DOWN:  return 270
        return 0

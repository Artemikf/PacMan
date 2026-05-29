"""
Тесты для GameMap и Vec2.
Используются: фикстуры, параметризация, маркеры.
"""
import pytest
from backend.core.game_map import (
    GameMap, Vec2, Fruit,
    WALL, DOT, ENERGIZER, EMPTY,
)


# ────────────────────────────────────────────────────────────
# 1. Тесты Vec2
# ────────────────────────────────────────────────────────────

@pytest.mark.map
def test_vec2_addition():
    """Сложение двух Vec2 работает корректно."""
    a = Vec2(1.0, 2.0)
    b = Vec2(3.0, 4.0)
    result = a + b
    assert result.x == 4.0
    assert result.y == 6.0


@pytest.mark.map
@pytest.mark.parametrize("x1,y1,x2,y2,expected", [
    (0, 0, 3, 4, 5.0),      # египетский треугольник 3-4-5
    (0, 0, 0, 0, 0.0),      # одна точка
    (1, 1, 4, 5, 5.0),      # смещённые координаты
])
def test_vec2_distance(x1, y1, x2, y2, expected):
    """distance_to() считает евклидово расстояние (параметризация)."""
    a = Vec2(float(x1), float(y1))
    b = Vec2(float(x2), float(y2))
    assert abs(a.distance_to(b) - expected) < 1e-9


@pytest.mark.map
def test_vec2_from_grid():
    """from_grid() переводит координаты сетки в пиксели."""
    v = Vec2.from_grid(0, 0, 32)
    assert v.x == 16  # 0 * 32 + 32 // 2
    assert v.y == 16


@pytest.mark.map
def test_vec2_to_grid():
    """to_grid() переводит пиксели обратно в координаты сетки."""
    v = Vec2(48.0, 80.0)
    row, col = v.to_grid(32)
    assert row == 2
    assert col == 1


# ────────────────────────────────────────────────────────────
# 2. Тесты GameMap (используем фикстуру game_map из conftest.py)
# ────────────────────────────────────────────────────────────

@pytest.mark.map
def test_corner_is_wall(game_map):
    """Угол лабиринта (0,0) — всегда стена."""
    assert game_map.is_wall(0, 0) is True


@pytest.mark.map
def test_inner_cell_not_always_wall(game_map):
    """Внутренние ячейки могут быть не стеной."""
    assert game_map.is_wall(1, 1) is False


@pytest.mark.map
def test_outside_bounds_is_wall(game_map):
    """Клетки за пределами карты — стена (безопасная граница)."""
    assert game_map.is_wall(-1, -1) is True
    assert game_map.is_wall(999, 999) is True


@pytest.mark.map
def test_tile_outside_returns_wall_value(game_map):
    """tile_at() за пределами карты возвращает WALL."""
    assert game_map.tile_at(-1, -1) == WALL


@pytest.mark.map
def test_total_dots_positive(game_map):
    """На карте должны быть точки."""
    assert game_map.total_dots > 0


@pytest.mark.map
def test_consume_dot_removes_it(game_map):
    """consume_dot() на ячейке с точкой возвращает True и удаляет точку."""
    # Строка 1, колонка 1 по базовой карте — DOT (значение 1)
    pos = Vec2(48.0, 48.0)  # tile(1,1): x=1*32+16=48, но to_grid вернёт (1,1)
    # Найдём первую DOT-ячейку
    dot_pos = None
    for r in range(game_map.rows):
        for c in range(game_map.cols):
            if game_map.grid[r][c] == DOT:
                dot_pos = Vec2(
                    float(c * game_map.TILE_SIZE + 1),
                    float(r * game_map.TILE_SIZE + 1),
                )
                break
        if dot_pos:
            break

    result = game_map.consume_dot(dot_pos)
    assert result is True


@pytest.mark.map
def test_consume_dot_on_wall_returns_false(game_map):
    """consume_dot() на стене возвращает False."""
    wall_pos = Vec2(1.0, 1.0)  # tile(0,0) — стена
    result = game_map.consume_dot(wall_pos)
    assert result is False


@pytest.mark.map
def test_all_dots_eaten_initially_false(game_map):
    """Сразу после создания карты не все точки съедены."""
    assert game_map.all_dots_eaten() is False


@pytest.mark.map
def test_pacman_start_property(game_map):
    """pacman_start возвращает Vec2."""
    start = game_map.pacman_start
    assert isinstance(start, Vec2)


@pytest.mark.map
def test_ghost_starts_length(game_map):
    """ghost_starts возвращает 4 позиции."""
    starts = game_map.ghost_starts
    assert len(starts) == 4


@pytest.mark.map
def test_pixel_dimensions(game_map):
    """pixel_width и pixel_height — положительные числа."""
    assert game_map.pixel_width() > 0
    assert game_map.pixel_height() > 0


# ────────────────────────────────────────────────────────────
# 3. Параметризация — разные уровни карты
# ────────────────────────────────────────────────────────────

@pytest.mark.map
@pytest.mark.parametrize("level", [1, 2, 3])
def test_map_created_for_each_level(level):
    """GameMap создаётся без ошибок для всех уровней."""
    gm = GameMap(level=level)
    assert gm.level == level
    assert gm.total_dots > 0


# ────────────────────────────────────────────────────────────
# 4. Тесты Fruit
# ────────────────────────────────────────────────────────────

@pytest.mark.map
def test_fruit_collides_when_close():
    """Фрукт столкнулся, если Пакман близко."""
    fruit = Fruit(Vec2(100.0, 100.0), points=100)
    close_pos = Vec2(105.0, 100.0)  # 5 пикселей — меньше радиуса 12
    assert fruit.collides_with(close_pos) is True


@pytest.mark.map
def test_fruit_no_collide_when_far():
    """Фрукт не столкнулся, если Пакман далеко."""
    fruit = Fruit(Vec2(100.0, 100.0), points=100)
    far_pos = Vec2(200.0, 200.0)
    assert fruit.collides_with(far_pos) is False


@pytest.mark.map
def test_fruit_collect_returns_points():
    """collect() возвращает очки и деактивирует фрукт."""
    fruit = Fruit(Vec2(0.0, 0.0), points=300)
    pts = fruit.collect()
    assert pts == 300
    assert fruit.active is False


@pytest.mark.map
def test_fruit_expires_over_time():
    """Фрукт деактивируется после истечения таймера."""
    fruit = Fruit(Vec2(0.0, 0.0), timer=1.0)
    fruit.update(dt=2.0)  # прошло 2 секунды
    assert fruit.active is False

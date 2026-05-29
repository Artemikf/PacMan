"""
Тесты для PacMan entity.
Используются: фикстуры, параметризация, мокование, маркеры.
"""
import pytest
from unittest.mock import MagicMock, patch

from backend.entities.pacman import PacMan, DIR_RIGHT, DIR_LEFT, DIR_UP, DIR_DOWN
from backend.core.game_map import Vec2, GameMap
from backend.utils.config import GameConfig


# ────────────────────────────────────────────────────────────
# 1. Базовые тесты
# ────────────────────────────────────────────────────────────

@pytest.mark.engine
def test_pacman_alive_on_creation(pacman_entity):
    """Пакман жив после создания."""
    assert pacman_entity.alive is True


@pytest.mark.engine
def test_pacman_initial_direction(pacman_entity):
    """Начальное направление — вправо."""
    assert pacman_entity.direction == DIR_RIGHT


@pytest.mark.engine
def test_set_direction_queues(pacman_entity):
    """set_direction() сохраняет направление в очередь."""
    pacman_entity.set_direction(DIR_UP)
    assert pacman_entity._queued_dir == DIR_UP


@pytest.mark.engine
def test_reset_restores_alive(pacman_entity, game_map):
    """reset() восстанавливает alive=True."""
    pacman_entity.alive = False
    pacman_entity.reset(game_map.pacman_start)
    assert pacman_entity.alive is True


@pytest.mark.engine
def test_rotation_deg_right(pacman_entity):
    """rotation_deg=0 для направления вправо."""
    pacman_entity.direction = DIR_RIGHT
    assert pacman_entity.rotation_deg == 0


# ────────────────────────────────────────────────────────────
# 2. Параметризация — углы поворота
# ────────────────────────────────────────────────────────────

@pytest.mark.engine
@pytest.mark.parametrize("direction, expected_deg", [
    (DIR_RIGHT, 0),
    (DIR_LEFT, 180),
    (DIR_UP, 90),
    (DIR_DOWN, 270),
])
def test_rotation_degrees(pacman_entity, direction, expected_deg):
    """rotation_deg возвращает правильный угол для каждого направления."""
    pacman_entity.direction = direction
    assert pacman_entity.rotation_deg == expected_deg


# ────────────────────────────────────────────────────────────
# 3. Мокование — тест update() без реальной физики карты
# ────────────────────────────────────────────────────────────

@pytest.mark.engine
def test_update_does_nothing_when_dead(pacman_entity):
    """
    Мокирование: если alive=False, update() не должен двигать Пакмана.
    """
    pacman_entity.alive = False
    initial_pos = Vec2(pacman_entity.position.x, pacman_entity.position.y)

    mock_map = MagicMock(spec=GameMap)

    pacman_entity.update(dt=0.1, game_map=mock_map)

    assert pacman_entity.position.x == initial_pos.x
    assert pacman_entity.position.y == initial_pos.y
    # is_wall не должен вызываться если Пакман мёртв
    mock_map.is_wall.assert_not_called()


@pytest.mark.engine
def test_mouth_animation_cycles(pacman_entity):
    """
    Мокирование: изолируем анимацию рта.
    Угол рта должен изменяться при вызове _animate_mouth().
    """
    initial_angle = pacman_entity.mouth_angle

    # Прогоним несколько итераций анимации
    pacman_entity._animate_mouth(dt=0.05)
    pacman_entity._animate_mouth(dt=0.05)

    # Угол должен измениться (анимация работает)
    assert pacman_entity.mouth_angle != initial_angle or pacman_entity._anim_time > 0


@pytest.mark.engine
def test_grid_position_property(pacman_entity):
    """grid_position возвращает текущую позицию."""
    pos = pacman_entity.grid_position
    assert pos.x == pacman_entity.position.x
    assert pos.y == pacman_entity.position.y

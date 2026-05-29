"""
Тесты для Ghost entity.
Используются: фикстуры, параметризация, мокование, маркеры.
"""
import pytest
from unittest.mock import MagicMock, patch

from backend.entities.ghost import Ghost, GhostMode, GhostPersonality
from backend.core.game_map import Vec2, GameMap
from backend.utils.config import GameConfig


# ────────────────────────────────────────────────────────────
# 1. Базовые тесты (используем фикстуру chaser_ghost)
# ────────────────────────────────────────────────────────────

@pytest.mark.ghost
def test_initial_mode_is_scatter(chaser_ghost):
    """Призрак начинает в режиме SCATTER."""
    assert chaser_ghost.mode == GhostMode.SCATTER


@pytest.mark.ghost
def test_frighten_sets_mode(chaser_ghost):
    """frighten() переводит призрака в режим FRIGHTENED."""
    chaser_ghost.frighten(5.0)
    assert chaser_ghost.mode == GhostMode.FRIGHTENED


@pytest.mark.ghost
def test_frightened_property(chaser_ghost):
    """is_frightened возвращает True после frighten()."""
    chaser_ghost.frighten(5.0)
    assert chaser_ghost.is_frightened is True


@pytest.mark.ghost
def test_die_sets_eaten_mode(chaser_ghost):
    """die() переводит призрака в режим EATEN."""
    chaser_ghost.die()
    assert chaser_ghost.is_eaten is True


@pytest.mark.ghost
def test_reset_restores_position(chaser_ghost):
    """reset() возвращает призрака на стартовую позицию."""
    chaser_ghost.position = Vec2(999.0, 999.0)
    chaser_ghost.reset()
    assert chaser_ghost.position.x == chaser_ghost._start.x
    assert chaser_ghost.position.y == chaser_ghost._start.y


@pytest.mark.ghost
def test_reset_restores_mode(chaser_ghost):
    """reset() возвращает режим SCATTER."""
    chaser_ghost.die()
    chaser_ghost.reset()
    assert chaser_ghost.mode == GhostMode.SCATTER


# ────────────────────────────────────────────────────────────
# 2. Параметризация — все типы призраков
# ────────────────────────────────────────────────────────────

@pytest.mark.ghost
@pytest.mark.parametrize("personality", [
    GhostPersonality.CHASER,
    GhostPersonality.AMBUSHER,
    GhostPersonality.FICKLE,
    GhostPersonality.COWARD,
])
def test_all_personalities_can_be_frightened(personality):
    """Любой призрак может перейти в режим FRIGHTENED (параметризация)."""
    ghost = Ghost(Vec2(0, 0), personality, 1.0, GameConfig())
    ghost.frighten(7.0)
    assert ghost.mode == GhostMode.FRIGHTENED


@pytest.mark.ghost
@pytest.mark.parametrize("speed_mult", [0.5, 1.0, 1.5, 2.0])
def test_effective_speed_at_different_multipliers(speed_mult):
    """
    Эффективная скорость в нормальном режиме = base_speed (параметризация).
    """
    config = GameConfig(ghost_speed=100.0)
    ghost = Ghost(Vec2(0, 0), GhostPersonality.CHASER, speed_mult, config)
    # base_speed = config.ghost_speed * speed_mult
    assert ghost.base_speed == config.ghost_speed * speed_mult


@pytest.mark.ghost
@pytest.mark.parametrize("duration, should_be_frightened", [
    (5.0, True),
    (0.1, True),
])
def test_frighten_duration(duration, should_be_frightened):
    """
    Призрак напуган сразу после frighten() с любой положительной длительностью.
    """
    ghost = Ghost(Vec2(0, 0), GhostPersonality.CHASER, 1.0, GameConfig())
    ghost.frighten(duration)
    assert ghost.is_frightened == should_be_frightened


# ────────────────────────────────────────────────────────────
# 3. Тест на столкновение
# ────────────────────────────────────────────────────────────

@pytest.mark.ghost
def test_collides_when_close():
    """collides_with() True, если объект рядом (меньше COLLISION_RADIUS)."""
    ghost = Ghost(Vec2(100, 100), GhostPersonality.CHASER, 1.0, GameConfig())
    nearby = Vec2(105, 100)  # 5 пикселей < COLLISION_RADIUS (12)
    assert ghost.collides_with(nearby) is True


@pytest.mark.ghost
def test_no_collision_when_far():
    """collides_with() False, если объект далеко."""
    ghost = Ghost(Vec2(100, 100), GhostPersonality.CHASER, 1.0, GameConfig())
    far = Vec2(500, 500)
    assert ghost.collides_with(far) is False


# ────────────────────────────────────────────────────────────
# 4. Мокование — тест update() без реальной карты
# ────────────────────────────────────────────────────────────

@pytest.mark.ghost
def test_frightened_timer_decrements(chaser_ghost):
    """
    Мокирование: подменяем _move_toward и _compute_target заглушками,
    чтобы проверить только логику уменьшения таймера испуга.
    """
    chaser_ghost.frighten(5.0)

    mock_map = MagicMock(spec=GameMap)
    mock_map.rows = 22
    mock_map.cols = 21
    mock_map.is_wall.return_value = False

    # Мокируем внутренние методы чтобы не зависеть от карты
    with patch.object(chaser_ghost, '_move_toward'):
        chaser_ghost._update_mode(dt=2.0)

    assert chaser_ghost._frighten_timer == pytest.approx(3.0)


@pytest.mark.ghost
def test_frightened_expires_and_returns_to_scatter(chaser_ghost):
    """
    После истечения таймера испуга призрак возвращается в SCATTER.
    Мокируем _move_toward чтобы изолировать логику режима.
    """
    chaser_ghost.frighten(1.0)

    with patch.object(chaser_ghost, '_move_toward'):
        chaser_ghost._update_mode(dt=2.0)  # 2 > 1 — таймер истёк

    assert chaser_ghost.mode == GhostMode.SCATTER


@pytest.mark.ghost
def test_eaten_ghost_does_not_become_frightened(chaser_ghost):
    """
    Мокирование сценария: съеденный призрак не может испугаться.
    """
    chaser_ghost.die()  # EATEN
    chaser_ghost.frighten(5.0)  # не должно сработать
    assert chaser_ghost.mode == GhostMode.EATEN

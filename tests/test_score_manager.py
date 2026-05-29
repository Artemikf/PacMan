"""
Тесты для ScoreManager.
Используются: фикстуры, параметризация, мокование, маркеры.
"""
import json
import pytest
from unittest.mock import patch, MagicMock

from backend.core.score_manager import (
    ScoreManager,
    DOT_POINTS,
    ENERGIZER_POINTS,
    GHOST_BASE_POINTS,
)


# ────────────────────────────────────────────────────────────
# 1. БАЗОВЫЕ ТЕСТЫ (фикстура score_manager из conftest.py)
# ────────────────────────────────────────────────────────────

@pytest.mark.score
def test_initial_score_is_zero(score_manager):
    """Начальный счёт должен быть 0."""
    assert score_manager.score == 0


@pytest.mark.score
def test_initial_lives(score_manager):
    """Начальное количество жизней = 3."""
    assert score_manager.lives == ScoreManager.STARTING_LIVES


@pytest.mark.score
def test_add_dot(score_manager):
    """add_dot() прибавляет DOT_POINTS к счёту."""
    score_manager.add_dot()
    assert score_manager.score == DOT_POINTS


@pytest.mark.score
def test_add_energizer(score_manager):
    """add_energizer() прибавляет ENERGIZER_POINTS."""
    score_manager.add_energizer()
    assert score_manager.score == ENERGIZER_POINTS


@pytest.mark.score
def test_lose_life_decrements(score_manager):
    """lose_life() уменьшает количество жизней на 1."""
    before = score_manager.lives
    score_manager.lose_life()
    assert score_manager.lives == before - 1


@pytest.mark.score
def test_lives_never_go_below_zero(score_manager):
    """Жизни не могут стать отрицательными."""
    for _ in range(10):
        score_manager.lose_life()
    assert score_manager.lives >= 0


@pytest.mark.score
def test_reset_clears_score_and_lives(score_manager):
    """reset() обнуляет счёт и восстанавливает жизни."""
    score_manager.add_dot()
    score_manager.lose_life()

    score_manager.reset()

    assert score_manager.score == 0
    assert score_manager.lives == ScoreManager.STARTING_LIVES


# ────────────────────────────────────────────────────────────
# 2. ПАРАМЕТРИЗАЦИЯ — несколько точек подряд
# ────────────────────────────────────────────────────────────

@pytest.mark.score
@pytest.mark.parametrize("dots, expected_score", [
    (1, DOT_POINTS * 1),
    (2, DOT_POINTS * 2),
    (5, DOT_POINTS * 5),
    (10, DOT_POINTS * 10),
])
def test_multiple_dots(score_manager, dots, expected_score):
    """Счёт за N точек = N * DOT_POINTS (параметризация)."""
    for _ in range(dots):
        score_manager.add_dot()
    assert score_manager.score == expected_score


@pytest.mark.score
@pytest.mark.parametrize("combo, expected_pts", [
    (1, GHOST_BASE_POINTS * 1),   # 200
    (2, GHOST_BASE_POINTS * 2),   # 400
    (3, GHOST_BASE_POINTS * 4),   # 800
    (4, GHOST_BASE_POINTS * 8),   # 1600
])
def test_ghost_combo_multiplier(combo, expected_pts, score_manager):
    """Каждый следующий съеденный призрак даёт удвоенные очки (параметризация)."""
    total = 0
    for i in range(combo):
        pts = score_manager.add_ghost_eaten()
        total += pts
    # Проверяем очки за ПОСЛЕДНЕГО съеденного призрака
    assert pts == expected_pts


# Независимый тест комбо без параметризации (чтобы не зависеть от фикстуры dots)
@pytest.mark.score
def test_ghost_combo_sequence(score_manager):
    """Первый призрак — 200, второй — 400, третий — 800."""
    assert score_manager.add_ghost_eaten() == GHOST_BASE_POINTS
    assert score_manager.add_ghost_eaten() == GHOST_BASE_POINTS * 2
    assert score_manager.add_ghost_eaten() == GHOST_BASE_POINTS * 4


@pytest.mark.score
def test_energizer_resets_combo(score_manager):
    """add_energizer() сбрасывает комбо призраков."""
    score_manager.add_ghost_eaten()
    score_manager.add_ghost_eaten()

    score_manager.add_energizer()           # комбо сбрасывается
    pts = score_manager.add_ghost_eaten()   # снова первый призрак

    assert pts == GHOST_BASE_POINTS


# ────────────────────────────────────────────────────────────
# 3. МОКОВАНИЕ — имитируем файловую систему
# ────────────────────────────────────────────────────────────

@pytest.mark.score
def test_high_score_saved_when_beaten():
    """
    Мокирование (mocking): заменяем реальную запись файла
    заглушкой, чтобы тест не зависел от файловой системы.
    patch() временно подменяет метод на MagicMock.
    """
    with patch("backend.core.score_manager.HIGH_SCORE_FILE") as mock_file:
        mock_file.exists.return_value = False
        mock_file.write_text = MagicMock()

        sm = ScoreManager()
        sm.add_points(500)

        # write_text должен был быть вызван (сохранение рекорда)
        mock_file.write_text.assert_called()


@pytest.mark.score
def test_high_score_loaded_from_file():
    """
    Мокирование: имитируем файл с сохранённым рекордом 9999.
    _load_high_score() должен вернуть это значение.
    """
    fake_data = json.dumps({"high_score": 9999})

    with patch("backend.core.score_manager.HIGH_SCORE_FILE") as mock_file:
        mock_file.exists.return_value = True
        mock_file.read_text.return_value = fake_data

        sm = ScoreManager()

        assert sm.high_score == 9999


@pytest.mark.score
def test_high_score_load_handles_corrupt_file():
    """
    Мокирование: файл есть, но содержит мусор — должен вернуть 0.
    """
    with patch("backend.core.score_manager.HIGH_SCORE_FILE") as mock_file:
        mock_file.exists.return_value = True
        mock_file.read_text.return_value = "not_valid_json{{{"

        sm = ScoreManager()

        assert sm.high_score == 0

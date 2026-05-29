"""
Тесты для GameEngine.
Используются: фикстуры, параметризация, мокование, маркеры.
"""
import pytest
from unittest.mock import MagicMock, patch

from backend.core.game_engine import GameEngine, GameState
from backend.utils.config import GameConfig


@pytest.fixture
def engine():
    """GameEngine с конфигом по умолчанию."""
    return GameEngine(GameConfig())


# ────────────────────────────────────────────────────────────
# 1. Базовые тесты состояния
# ────────────────────────────────────────────────────────────

@pytest.mark.engine
def test_initial_state_is_menu(engine):
    """Сразу после создания движок в состоянии MENU."""
    assert engine.state == GameState.MENU


@pytest.mark.engine
def test_start_game_sets_playing(engine):
    """start_game() переводит в PLAYING."""
    engine.start_game()
    assert engine.state == GameState.PLAYING


@pytest.mark.engine
def test_pause_from_playing(engine):
    """pause() из PLAYING переводит в PAUSED."""
    engine.start_game()
    engine.pause()
    assert engine.state == GameState.PAUSED


@pytest.mark.engine
def test_resume_from_paused(engine):
    """resume() из PAUSED возвращает в PLAYING."""
    engine.start_game()
    engine.pause()
    engine.resume()
    assert engine.state == GameState.PLAYING


@pytest.mark.engine
def test_pause_only_from_playing(engine):
    """pause() в состоянии MENU ничего не делает."""
    engine.pause()  # engine.state == MENU
    assert engine.state == GameState.MENU


@pytest.mark.engine
def test_restart_resets_level(engine):
    """restart() сбрасывает уровень до 1."""
    engine.start_game()
    engine.level = 3
    engine.restart()
    assert engine.level == 1


@pytest.mark.engine
def test_score_property(engine):
    """Свойство score возвращает число."""
    engine.start_game()
    assert isinstance(engine.score, int)


@pytest.mark.engine
def test_lives_property(engine):
    """Свойство lives = 3 в начале игры."""
    engine.start_game()
    assert engine.lives == 3


# ────────────────────────────────────────────────────────────
# 2. Параметризация — количество призраков
# ────────────────────────────────────────────────────────────

@pytest.mark.engine
@pytest.mark.parametrize("ghost_count", [1, 2, 3, 4])
def test_ghost_count_matches_config(ghost_count):
    """После start_game() количество призраков соответствует конфигу."""
    config = GameConfig(ghost_count=ghost_count)
    engine = GameEngine(config)
    engine.start_game()
    assert len(engine.ghosts) == ghost_count


# ────────────────────────────────────────────────────────────
# 3. Мокование — тест update() без реальной логики
# ────────────────────────────────────────────────────────────

@pytest.mark.engine
def test_update_not_called_when_paused(engine):
    """
    Мокирование: в состоянии PAUSED update() ничего не делает.
    Мы мокируем pacman.update, чтобы убедиться, что он НЕ вызывается.
    """
    engine.start_game()
    engine.pause()

    mock_pacman = MagicMock()
    engine.pacman = mock_pacman

    engine.update(dt=0.016)

    mock_pacman.update.assert_not_called()


@pytest.mark.engine
def test_update_calls_pacman_update_when_playing(engine):
    """
    Мокирование: в PLAYING состоянии pacman.update() ДОЛЖЕН вызываться.
    """
    engine.start_game()

    mock_pacman = MagicMock()
    mock_pacman.position = MagicMock()
    mock_pacman.grid_position = MagicMock()
    mock_pacman.alive = True
    engine.pacman = mock_pacman

    # Мокируем карту и призраков чтобы не упасть
    engine.game_map = MagicMock()
    engine.game_map.all_dots_eaten.return_value = False
    engine.game_map.consume_dot.return_value = False
    engine.game_map.consume_energizer.return_value = False
    engine.game_map.fruit = None
    engine.ghosts = []

    engine.update(dt=0.016)

    mock_pacman.update.assert_called_once_with(0.016, engine.game_map)

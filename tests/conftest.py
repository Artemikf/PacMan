import pytest

from backend.core.score_manager import ScoreManager
from backend.core.game_map import GameMap, Vec2
from backend.utils.config import GameConfig
from backend.entities.ghost import Ghost, GhostPersonality
from backend.entities.pacman import PacMan

@pytest.fixture
def score_manager():
    """Чистый ScoreManager перед каждым тестом."""
    return ScoreManager()


@pytest.fixture
def game_map():
    """Карта уровня 1."""
    return GameMap(level=1)


@pytest.fixture
def config():
    """Конфиг по умолчанию."""
    return GameConfig()



@pytest.fixture
def chaser_ghost(config):
    """Призрак-преследователь в начальной точке (0, 0)."""
    return Ghost(Vec2(0, 0), GhostPersonality.CHASER, 1.0, config)


@pytest.fixture
def pacman_entity(game_map, config):
    """Пакман на стартовой позиции карты."""
    return PacMan(game_map.pacman_start, config)

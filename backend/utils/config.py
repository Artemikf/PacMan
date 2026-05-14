from dataclasses import dataclass

@dataclass
class GameConfig:
    # Speeds (pixels/sec)
    pacman_speed: float = 150.0
    ghost_speed: float = 150.0
    ghost_speed_increase: float = 0.10   # множитель за уровень
    # Gameplay
    frighten_duration: float = 7.0       # секунды призраки остаются напуганными
    ghost_count: int = 4
    max_levels: int = 3
    # Display
    bg_color: str = "#000000"            # шестнадцатеричный цвет фона меню
    game_bg_color: str = "#000000"       # Шестнадцатеричный цвет фона в игре
    tile_size: int = 32
    fps: int = 60
    window_title: str = "PacMan"
    # Audio
    mute: bool = False
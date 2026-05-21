from dataclasses import dataclass
import argparse

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

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> "GameConfig":
        preset = DIFFICULTY_PRESETS.get(args.difficulty, DIFFICULTY_PRESETS["normal"])
        return cls(
            pacman_speed=preset["pacman_speed"],
            ghost_speed=preset["ghost_speed"],
            frighten_duration=preset["frighten_duration"],
            ghost_speed_increase=preset["ghost_speed_increase"],
            bg_color=args.bg_color,
            game_bg_color=args.game_bg_color,
            max_levels=args.levels,
            mute=args.mute,
        )

DIFFICULTY_PRESETS = {
    "easy":   dict(ghost_speed=120, pacman_speed=160, frighten_duration=10.0, ghost_speed_increase=0.05),
    "normal": dict(ghost_speed=150, pacman_speed=150, frighten_duration=7.0,  ghost_speed_increase=0.10),
    "hard":   dict(ghost_speed=180, pacman_speed=140, frighten_duration=4.0,  ghost_speed_increase=0.15),
}

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="PacMan — Python/Pygame implementation")

    parser.add_argument(
        "--difficulty", choices=["easy", "normal", "hard"], default="normal",
        help="Game difficulty (default: normal)"
    )
    parser.add_argument(
        "--bg-color", default="#000000", metavar="HEX",
        help="Menu background colour as hex, e.g. #1a1a2e (default: #000000)"
    )
    parser.add_argument(
        "--game-bg-color", default="#000000", metavar="HEX",
        help="In-game background colour as hex (default: #000000)"
    )
    parser.add_argument(
        "--levels", type=int, default=3, metavar="N",
        help="Number of levels before victory screen (default: 3)"
    )
    parser.add_argument(
        "--mute", action="store_true",
        help="Disable all sound effects"
    )
    return parser.parse_args()



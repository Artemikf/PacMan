from enum import Enum, auto

# перечисление состояний
class GameState(Enum):
    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    VICTORY = auto()

# центральный игровой движок
class GameEngine:

    def __init__(self):
        self.state = GameState.MENU
        self.level = 1
        self._running = False

    # ─────────────────────── режими
    def start_game(self) -> None:
        self.state = GameState.PLAYING
        self._running = True

    def pause(self) -> None:
        if self.state == GameState.PLAYING:
            self.state = GameState.PAUSED

    def resume(self) -> None:
        if self.state == GameState.PAUSED:
            self.state = GameState.PLAYING

    def restart(self) -> None:
        self.level = 1







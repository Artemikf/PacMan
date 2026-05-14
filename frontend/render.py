from __future__ import annotations
import math
import pygame

from backend.core.game_map import GameMap, Vec2, WALL, DOT, ENERGIZER, GHOST_HOUSE
from backend.entities.pacman import PacMan
from backend.entities.ghost import Ghost, GhostMode, GhostPersonality
from backend.core.game_engine import GameState
from backend.utils.config import GameConfig




# ── Colour palette ────────────────────────────────────────────────────────────
WHITE   = (255, 255, 255)
YELLOW  = (255, 220,  0)
BLUE    = ( 33,  33, 255)
LBLUE   = ( 80, 120, 255)  # wall highlight
BLACK   = (  0,   0,   0)
DARK    = ( 10,  10,  20)
RED     = (255,   0,   0)
CYAN    = (  0, 255, 255)
PINK    = (255, 184, 255)
ORANGE  = (255, 184,  82)
SCARED  = ( 30,  30, 220)   # frightened ghost body
SCARED2 = (255, 255, 255)   # flashing phase
DOT_CLR = (255, 200, 140)
ENRG_CLR= (255, 255, 180)
FRUIT_CLR=(255,  80,  80)

def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

class Renderer:
    HUD_HEIGHT = 48
    FONT_NAME  = None


    def __init__(self, config: GameConfig, game_map: GameMap):
        self.config = config
        self.tile   = game_map.TILE_SIZE
        self.cols   = game_map.cols
        self.rows   = game_map.rows
        self.width  = game_map.pixel_width()
        self.height = game_map.pixel_height() + self.HUD_HEIGHT
        self.bg_color      = _hex_to_rgb(config.bg_color)
        self.game_bg_color = _hex_to_rgb(config.game_bg_color)
        pygame.font.init()
        self.font_large = pygame.font.SysFont("monospace", 28, bold=True)
        self.font_small = pygame.font.SysFont("monospace", 18)
        self.font_tiny  = pygame.font.SysFont("monospace", 14)
        self.screen: pygame.Surface | None = None

    # ── Screen management ─────────────────────────────────────────────────────

    def init_screen(self) -> pygame.Surface:
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(self.config.window_title)
        return self.screen

    # ── Master draw ───────────────────────────────────────────────────────────

    def draw_game(
            self,
            surface: pygame.Surface,
            game_map: GameMap,
            pacman: PacMan,
            ghosts: list[Ghost],
            score: int,
            high_score: int,
            lives: int,
            level: int,
    ) -> None:
        surface.fill(self.game_bg_color)
        self._draw_maze(surface, game_map)
        self._draw_dots(surface, game_map)
        self._draw_fruit(surface, game_map)
        self._draw_pacman(surface, pacman)
        for ghost in ghosts:
            self._draw_ghost(surface, ghost)
        self._draw_hud(surface, score, high_score, lives, level)






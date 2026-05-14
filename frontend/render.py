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
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))  # type: ignore
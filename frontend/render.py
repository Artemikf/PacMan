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


    def draw_menu(self, surface: pygame.Surface, high_score: int) -> None:
        surface.fill(self.bg_color)
        # Title
        title = self.font_large.render("PAC-MAN", True, YELLOW)
        surface.blit(title, (self.width // 2 - title.get_width() // 2, 80))
        # Subtitle
        sub = self.font_small.render("Press ENTER to Start", True, WHITE)
        surface.blit(sub, (self.width // 2 - sub.get_width() // 2, 150))
        hs = self.font_small.render(f"High Score: {high_score}", True, CYAN)
        surface.blit(hs, (self.width // 2 - hs.get_width() // 2, 190))
        # Controls hint
        hints = [
            "Arrow Keys / WASD — Move",
            "P — Pause",
            "ESC — Menu",
        ]
        for i, hint in enumerate(hints):
            t = self.font_tiny.render(hint, True, (180, 180, 180))
            surface.blit(t, (self.width // 2 - t.get_width() // 2, 260 + i * 22))

    def draw_pause(self, surface: pygame.Surface) -> None:
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        surface.blit(overlay, (0, 0))
        txt = self.font_large.render("PAUSED", True, YELLOW)
        surface.blit(txt, (self.width // 2 - txt.get_width() // 2, self.height // 2 - 20))
        hint = self.font_small.render("Press P to resume", True, WHITE)
        surface.blit(hint, (self.width // 2 - hint.get_width() // 2, self.height // 2 + 30))

    def draw_game_over(self, surface: pygame.Surface, score: int) -> None:
        surface.fill(BLACK)
        txt = self.font_large.render("GAME OVER", True, RED)
        surface.blit(txt, (self.width // 2 - txt.get_width() // 2, self.height // 2 - 60))
        s = self.font_small.render(f"Score: {score}", True, WHITE)
        surface.blit(s, (self.width // 2 - s.get_width() // 2, self.height // 2))
        hint = self.font_small.render("ENTER — New Game   ESC — Menu", True, (160, 160, 160))
        surface.blit(hint, (self.width // 2 - hint.get_width() // 2, self.height // 2 + 50))

    def draw_victory(self, surface: pygame.Surface, score: int) -> None:
        surface.fill(DARK)
        txt = self.font_large.render("YOU WIN!", True, YELLOW)
        surface.blit(txt, (self.width // 2 - txt.get_width() // 2, self.height // 2 - 60))
        s = self.font_small.render(f"Score: {score}", True, WHITE)
        surface.blit(s, (self.width // 2 - s.get_width() // 2, self.height // 2))
        hint = self.font_small.render("ENTER — New Game   ESC — Menu", True, (160, 160, 160))
        surface.blit(hint, (self.width // 2 - hint.get_width() // 2, self.height // 2 + 50))

    # ── Maze ──────────────────────────────────────────────────────────────────

    def _draw_maze(self, surface: pygame.Surface, game_map: GameMap) -> None:
        ts = self.tile
        for row in range(game_map.rows):
            for col in range(game_map.cols):
                cell = game_map.tile_at(row, col)
                x, y = col * ts, row * ts + self.HUD_HEIGHT
                if cell == WALL:
                    rect = pygame.Rect(x, y, ts, ts)
                    pygame.draw.rect(surface, BLUE, rect)
                    # Inner highlight
                    inner = rect.inflate(-4, -4)
                    pygame.draw.rect(surface, LBLUE, inner, 1)
                elif cell == GHOST_HOUSE:
                    rect = pygame.Rect(x, y, ts, ts)
                    pygame.draw.rect(surface, (40, 10, 40), rect)

    # ── Dots and energizers ───────────────────────────────────────────────────

    def _draw_dots(self, surface: pygame.Surface, game_map: GameMap) -> None:
        ts = self.tile
        for row in range(game_map.rows):
            for col in range(game_map.cols):
                cell = game_map.tile_at(row, col)
                cx = col * ts + ts // 2
                cy = row * ts + ts // 2 + self.HUD_HEIGHT
                if cell == DOT:
                    pygame.draw.circle(surface, DOT_CLR, (cx, cy), 3)
                elif cell == ENERGIZER:
                    pygame.draw.circle(surface, ENRG_CLR, (cx, cy), 8)
                    # Glow ring
                    pygame.draw.circle(surface, YELLOW, (cx, cy), 8, 1)

    # ── Fruit ─────────────────────────────────────────────────────────────────

    def _draw_fruit(self, surface: pygame.Surface, game_map: GameMap) -> None:
        if not game_map.fruit or not game_map.fruit.active:
            return
        fx = int(game_map.fruit.position.x)
        fy = int(game_map.fruit.position.y) + self.HUD_HEIGHT
        pygame.draw.circle(surface, FRUIT_CLR, (fx, fy), 10)
        # Leaf
        pygame.draw.line(surface, (0, 200, 0), (fx, fy - 10), (fx + 8, fy - 18), 2)


 # ── PacMan ────────────────────────────────────────────────────────────────

    def _draw_pacman(self, surface: pygame.Surface, pacman: PacMan) -> None:
        cx = int(pacman.position.x)
        cy = int(pacman.position.y) + self.HUD_HEIGHT
        radius = self.tile // 2 - 2
        angle  = pacman.mouth_angle
        rot    = pacman.rotation_deg

        # Draw filled arc (pie slice cut out for mouth)
        start_deg = rot + angle
        end_deg   = rot + 360 - angle
        self._draw_pacman_arc(surface, cx, cy, radius, start_deg, end_deg, YELLOW)
        # Eye
        eye_angle = math.radians(rot + 70)
        ex = cx + int(math.cos(eye_angle) * radius * 0.5)
        ey = cy - int(math.sin(eye_angle) * radius * 0.5)
        pygame.draw.circle(surface, BLACK, (ex, ey), 2)

    @staticmethod
    def _draw_pacman_arc(
        surface: pygame.Surface,
        cx: int, cy: int, radius: int,
        start_deg: float, end_deg: float,
        color: tuple,
    ) -> None:
        """Draw a filled pie/arc shape."""
        points = [(cx, cy)]
        for deg in range(int(start_deg), int(end_deg) + 1, 3):
            rad = math.radians(deg)
            x = cx + int(math.cos(rad) * radius)
            y = cy - int(math.sin(rad) * radius)
            points.append((x, y))
        if len(points) >= 3:
            pygame.draw.polygon(surface, color, points)

# ── Ghost ─────────────────────────────────────────────────────────────────

    def _draw_ghost(self, surface: pygame.Surface, ghost: Ghost) -> None:
        cx = int(ghost.position.x)
        cy = int(ghost.position.y) + self.HUD_HEIGHT
        r  = self.tile // 2 - 2

        if ghost.mode == GhostMode.FRIGHTENED:
            # Blue body, flashing when almost over
            body_color = SCARED
        elif ghost.mode == GhostMode.EATEN:
            # Just eyes
            self._draw_ghost_eyes(surface, cx, cy, r)
            return
        else:
            body_color = ghost.color

        # Body: top semicircle + rectangle bottom with wavy skirt
        body_rect = pygame.Rect(cx - r, cy - r, r * 2, r * 2)
        pygame.draw.ellipse(surface, body_color, body_rect)
        lower_rect = pygame.Rect(cx - r, cy, r * 2, r)
        pygame.draw.rect(surface, body_color, lower_rect)

        # Wavy skirt (3 bumps)
        bump_r = r // 3
        for i in range(3):
            bx = cx - r + bump_r + i * bump_r * 2
            by = cy + r
            pygame.draw.circle(surface, body_color, (bx, by), bump_r)

        # Eyes
        self._draw_ghost_eyes(surface, cx, cy, r)

        # Frightened face
        if ghost.mode == GhostMode.FRIGHTENED:
            # Squiggly mouth
            for i in range(-r + 4, r - 4, 4):
                h = 3 if (i // 4) % 2 == 0 else -3
                pygame.draw.circle(surface, WHITE, (cx + i, cy + 4 + h), 2)

    @staticmethod
    def _draw_ghost_eyes(surface: pygame.Surface, cx: int, cy: int, r: int) -> None:
        for sign in (-1, 1):
            ex = cx + sign * r // 3
            ey = cy - r // 4
            pygame.draw.circle(surface, WHITE, (ex, ey), r // 4)
            pygame.draw.circle(surface, (0, 0, 200), (ex + sign, ey + 1), r // 6)
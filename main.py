import sys
import pygame

from backend.utils.config import parse_args, GameConfig
from backend.core.game_engine import GameEngine, GameState
from frontend.render import Renderer
from frontend.input_handler import InputHandler
from frontend.sound_manager import SoundManager


def main() -> None:
    args   = parse_args()
    config = GameConfig.from_args(args)

    pygame.init()
    engine = GameEngine(config)
    engine.start_game()  # initialises map so Renderer can measure dimensions

    renderer = Renderer(config, engine.game_map)
    screen   = renderer.init_screen()
    inputs   = InputHandler()
    sounds   = SoundManager(config.mute)
    clock    = pygame.time.Clock()

    # Track previous state to trigger one-shot sounds
    _prev_score = 0
    _prev_lives = engine.lives

    while True:
        dt = clock.tick(config.fps) / 1000.0  # seconds
        inputs.poll()

        # ── Global exit
        if inputs.quit_requested:
            pygame.quit()
            sys.exit()

        # ── State machine input
        state = engine.state

        if state == GameState.MENU:
            if inputs.enter_pressed:
                engine.start_game()
            renderer.draw_menu(screen, engine.high_score)

        elif state == GameState.PLAYING:
            direction = inputs.get_direction()
            if direction:
                engine.pacman.set_direction(direction)
            if inputs.pause_pressed:
                engine.pause()
            if inputs.escape_pressed:
                engine.state = GameState.MENU

            engine.update(dt)
            engine.game_map.update(dt)

            # One-shot sounds
            if engine.score > _prev_score:
                if engine.score - _prev_score >= 50:
                    sounds.play_energizer()
                else:
                    sounds.play_dot()
            if engine.lives < _prev_lives:
                sounds.play_death()
            _prev_score = engine.score
            _prev_lives = engine.lives

            renderer.draw_game(
                screen,
                engine.game_map,
                engine.pacman,
                engine.ghosts,
                engine.score,
                engine.high_score,
                engine.lives,
                engine.level,
            )

        elif state == GameState.PAUSED:
            # Keep the last game frame visible
            renderer.draw_pause(screen)
            if inputs.pause_pressed:
                engine.resume()
            if inputs.escape_pressed:
                engine.state = GameState.MENU

        elif state == GameState.GAME_OVER:
            renderer.draw_game_over(screen, engine.score)
            if inputs.enter_pressed:
                engine.restart()
                _prev_score = 0
                _prev_lives = engine.lives
            if inputs.escape_pressed:
                engine.state = GameState.MENU

        elif state == GameState.VICTORY:
            sounds.play_victory()
            renderer.draw_victory(screen, engine.score)
            if inputs.enter_pressed:
                engine.restart()
                _prev_score = 0
                _prev_lives = engine.lives
            if inputs.escape_pressed:
                engine.state = GameState.MENU

        pygame.display.flip()


if __name__ == "__main__":
    main()

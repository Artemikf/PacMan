from __future__ import annotations
import pygame
from backend.entities.pacman import DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT

class InputHandler:


    def __init__(self):
        self._events: list[pygame.event.Event] = []

    def poll(self) -> None:
        self._events = pygame.event.get()


    @property
    def quit_requested(self) -> bool:
        return any(e.type == pygame.QUIT for e in self._events)

    @property
    def enter_pressed(self) -> bool:
        return any(
            e.type == pygame.KEYDOWN and e.key in (pygame.K_RETURN, pygame.K_KP_ENTER)
            for e in self._events
        )

    @property
    def escape_pressed(self) -> bool:
        return any(
            e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE
            for e in self._events
        )

    @property
    def pause_pressed(self) -> bool:
        return any(
            e.type == pygame.KEYDOWN and e.key == pygame.K_p
            for e in self._events
        )

    def get_direction(self):

        for e in self._events:
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_UP, pygame.K_w):
                    return DIR_UP
                if e.key in (pygame.K_DOWN, pygame.K_s):
                    return DIR_DOWN
                if e.key in (pygame.K_LEFT, pygame.K_a):
                    return DIR_LEFT
                if e.key in (pygame.K_RIGHT, pygame.K_d):
                    return DIR_RIGHT
        return None



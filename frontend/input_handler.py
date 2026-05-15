from __future__ import annotations
import pygame
from backend.entities.pacman import DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT

class InputHandler:


    def __init__(self):
        self._events: list[pygame.event.Event] = []

    def poll(self) -> None:
        self._events = pygame.event.get()




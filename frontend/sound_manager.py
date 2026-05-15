from __future__ import annotations
import math
import array
import pygame

def _sine_wave(freq: float, duration_ms: int, volume: float = 0.4, sample_rate: int = 22050) -> pygame.mixer.Sound:
    n_samples = int(sample_rate * duration_ms / 1000)
    buf = array.array("h", [0] * n_samples)
    max_amp = int(32767 * volume)
    for i in range(n_samples):
        buf[i] = int(max_amp * math.sin(2 * math.pi * freq * i / sample_rate))
    sound = pygame.mixer.Sound(buffer=buf)
    return sound









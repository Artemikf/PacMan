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
class SoundManager:
    def __init__(self, mute: bool = False):
        self._mute = mute
        self._ready = False
        if mute:
            return
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
            self._dot    = _sine_wave(440,  60, 0.2)
            self._enrg   = _sine_wave(880, 200, 0.4)
            self._ghost  = _sine_wave(660, 150, 0.35)
            self._death  = _sine_wave(200, 600, 0.5)
            self._win    = _sine_wave(1046, 400, 0.45)
            self._ready  = True
        except Exception:
            self._ready = False

    def play_dot(self)    -> None: self._play(self._dot)
    def play_energizer(self) -> None: self._play(self._enrg)
    def play_ghost_eaten(self) -> None: self._play(self._ghost)
    def play_death(self)  -> None: self._play(self._death)
    def play_victory(self) -> None: self._play(self._win)

    def _play(self, sound) -> None:
        if self._ready and not self._mute:
            try:
                sound.play()
            except Exception:
                pass










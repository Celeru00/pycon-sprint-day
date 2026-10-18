import random

import pygame

from glitch_runner.config import BLACK, GLITCH_COLOR, SCREEN_HEIGHT, SCREEN_WIDTH
from glitch_runner.domain.glitches import ScreenEffects
from glitch_runner.domain.level import LevelGlitch

COLOR_OVERLAY_ALPHA = 50
STATIC_ALPHA = 100


class ScreenEffectsRenderer:
    def __init__(self) -> None:
        self.font = pygame.font.SysFont(None, 48)
        self._snapshot: pygame.Surface | None = None

    def apply(self, surface: pygame.Surface, effects: ScreenEffects, notice: str | None) -> None:
        size = surface.get_size()
        if self._snapshot is None or self._snapshot.get_size() != size:
            self._snapshot = pygame.Surface(size)
        self._snapshot.blit(surface, (0, 0))

        if effects.color_shift != (0, 0, 0):
            overlay = pygame.Surface(size)
            overlay.fill(tuple(max(0, min(255, 128 + c)) for c in effects.color_shift))
            overlay.set_alpha(COLOR_OVERLAY_ALPHA)
            surface.blit(overlay, (0, 0))

        if effects.shake_amount > 0:
            shaken = pygame.Surface(size)
            shaken.fill(BLACK)
            shaken.blit(self._snapshot, effects.offset)
            surface.blit(shaken, (0, 0))

        if effects.pixel_size > 1:
            width, height = size
            small = pygame.transform.scale(
                surface, (width // effects.pixel_size, height // effects.pixel_size)
            )
            surface.blit(pygame.transform.scale(small, size), (0, 0))

        if notice:
            text = self.font.render(notice, True, GLITCH_COLOR)
            surface.blit(text, text.get_rect(center=(SCREEN_WIDTH // 2, 50)))


def apply_level_glitch(surface: pygame.Surface, effect: LevelGlitch | None) -> None:
    if effect is LevelGlitch.COLOR_SHIFT:
        surface.blit(surface.copy(), (random.randint(3, 8), 0))
    elif effect is LevelGlitch.STATIC:
        _draw_static(surface)


def _draw_static(surface: pygame.Surface) -> None:
    height = random.randint(5, 20)
    y = random.randint(0, SCREEN_HEIGHT - height)
    noise = pygame.Surface((SCREEN_WIDTH, height))
    for x in range(0, SCREEN_WIDTH, 2):
        for row in range(0, height, 2):
            if random.random() < 0.5:
                color = (
                    random.randint(200, 255),
                    random.randint(200, 255),
                    random.randint(200, 255),
                )
                noise.set_at((x, row), color)
    noise.set_alpha(STATIC_ALPHA)
    surface.blit(noise, (0, y))

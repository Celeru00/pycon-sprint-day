import math
import random
from dataclasses import dataclass

import pygame

from glitch_runner.config import SCREEN_HEIGHT, SCREEN_WIDTH

LEVEL_COLORS = {
    1: (30, 30, 40),
    2: (35, 25, 45),
    3: (40, 25, 30),
    4: (45, 15, 45),
}
DEFAULT_LEVEL_COLOR = (50, 10, 20)
GRID_SIZE = 80
INTENSE_FROM_LEVEL = 4


@dataclass
class GlitchShape:
    x: int
    y: int
    width: int
    height: int
    color: tuple[int, int, int, int]
    lifetime: int
    age: int = 0

    @property
    def expired(self) -> bool:
        return self.age >= self.lifetime

    def faded_color(self) -> tuple[int, int, int, int]:
        alpha = int(255 * (1 - self.age / self.lifetime))
        return (*self.color[:3], alpha)


class Background:
    def __init__(self, level_number: int, image: pygame.Surface | None = None) -> None:
        self.level_number = level_number
        self.image = image
        self.color = LEVEL_COLORS.get(level_number, DEFAULT_LEVEL_COLOR)
        self.timer = 0
        self.lines: list[GlitchShape] = []
        self.blocks: list[GlitchShape] = []
        if level_number > 1:
            self._generate()

    @property
    def _intense(self) -> bool:
        return self.level_number >= INTENSE_FROM_LEVEL

    def update(self) -> None:
        self.timer += 1
        if self.level_number <= 1:
            return

        interval, chance = (90, 0.3) if self._intense else (180, 0.1)
        if self.timer >= interval:
            self.timer = 0
            if random.random() < chance:
                self._generate()

        for shape in self.lines + self.blocks:
            shape.age += 1
        self.lines = [s for s in self.lines if not s.expired]
        self.blocks = [s for s in self.blocks if not s.expired]

    def draw(self, surface: pygame.Surface) -> None:
        if self.image is not None:
            surface.blit(self.image, (0, 0))
            return

        surface.fill(self.color)
        if self.level_number <= 3:
            self._draw_grid(surface)
        elif self.level_number == 4:
            self._draw_wavy_grid(surface)
        else:
            self._draw_corrupted_grid(surface)

        for shape in self.lines + self.blocks:
            shape_surface = pygame.Surface((shape.width, shape.height), pygame.SRCALPHA)
            shape_surface.fill(shape.faded_color())
            surface.blit(shape_surface, (shape.x, shape.y))

    def _generate(self) -> None:
        self.lines = [self._random_line() for _ in range(self.level_number)]
        self.blocks = []
        if self._intense:
            self.blocks = [self._random_block() for _ in range(self.level_number - 2)]

    def _random_line(self) -> GlitchShape:
        y = random.randint(0, SCREEN_HEIGHT)
        width = random.randint(100, 300)
        x = random.randint(0, SCREEN_WIDTH - width)
        if self._intense:
            opacity = random.randint(20, 40)
            color = (*_random_light_rgb(), opacity)
            height = random.randint(1, 3)
        else:
            opacity = random.randint(10, 20)
            color = (200, 200, 200, opacity)
            height = 1
        return GlitchShape(x, y, width, height, color, random.randint(60, 180))

    def _random_block(self) -> GlitchShape:
        x = random.randint(0, SCREEN_WIDTH - 50)
        y = random.randint(0, SCREEN_HEIGHT - 50)
        width = random.randint(10, 30)
        height = random.randint(10, 30)
        opacity = random.randint(15, 35)
        color = (*_random_light_rgb(), opacity)
        return GlitchShape(x, y, width, height, color, random.randint(30, 120))

    def _draw_grid(self, surface: pygame.Surface) -> None:
        color = (255, 255, 255, self.level_number + 1)
        for x in range(0, SCREEN_WIDTH, GRID_SIZE):
            pygame.draw.line(surface, color, (x, 0), (x, SCREEN_HEIGHT), 1)
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            pygame.draw.line(surface, color, (0, y), (SCREEN_WIDTH, y), 1)

    def _draw_wavy_grid(self, surface: pygame.Surface) -> None:
        color = (255, 255, 255, 5)
        for x in range(0, SCREEN_WIDTH, GRID_SIZE):
            points = [(x, 0)] + [
                (x + self._wave(y), y) for y in range(GRID_SIZE, SCREEN_HEIGHT, GRID_SIZE)
            ]
            pygame.draw.lines(surface, color, False, points, 1)
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            points = [(0, y)] + [
                (x, y + self._wave(x)) for x in range(GRID_SIZE, SCREEN_WIDTH, GRID_SIZE)
            ]
            pygame.draw.lines(surface, color, False, points, 1)

    def _wave(self, position: int) -> float:
        return math.sin(position / 50 + self.timer / 15) * 3

    def _draw_corrupted_grid(self, surface: pygame.Surface) -> None:
        for x in range(0, SCREEN_WIDTH, GRID_SIZE):
            for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
                if random.random() < 0.7:
                    cell_color = tuple(min(255, c + random.randint(0, 20)) for c in self.color)
                    pygame.draw.rect(surface, cell_color, (x, y, GRID_SIZE, GRID_SIZE), 1)


def _random_light_rgb() -> tuple[int, int, int]:
    return (random.randint(150, 255), random.randint(150, 255), random.randint(150, 255))

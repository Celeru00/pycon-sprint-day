import math

import pygame

from glitch_runner.config import (
    DEBUG_MODE,
    ENEMY_COLOR,
    ENEMY_HEIGHT,
    ENEMY_WIDTH,
    EXIT_COLOR,
    PLATFORM_COLOR,
    WHITE,
)
from glitch_runner.domain.enemy import Enemy, EnemyType
from glitch_runner.domain.platform import Platform
from glitch_runner.domain.player import MAX_JUMPS, Player

ANIMATION_SPEED = 0.2
EXIT_PULSE_STEP = 0.1
PROJECTILE_COLOR = (255, 255, 0)
DEBUG_COLOR = (255, 0, 0)

Offset = tuple[int, int]


class PlayerSprite:
    def __init__(self, frames: dict[str, list[pygame.Surface]]) -> None:
        self.frames = frames
        self.state = "idle_right"
        self.frame = 0.0
        self.debug_font = pygame.font.SysFont(None, 24)

    @property
    def image(self) -> pygame.Surface:
        return self.frames[self.state][int(self.frame)]

    def advance(self, player: Player) -> None:
        state = _animation_state(player)
        if state != self.state:
            self.state = state
            self.frame = 0
        self.frame += ANIMATION_SPEED
        if self.frame >= len(self.frames[self.state]):
            self.frame = 0

    def draw(self, surface: pygame.Surface, player: Player, now: float) -> None:
        image = self.image
        if player.invincible and int(now * 10) % 2 == 0:
            image = image.copy()
            image.fill((255, 255, 255, 128), None, pygame.BLEND_RGBA_MULT)
        surface.blit(image, player.rect)

        if DEBUG_MODE:
            self._draw_debug(surface, player)

    def _draw_debug(self, surface: pygame.Surface, player: Player) -> None:
        pygame.draw.rect(surface, DEBUG_COLOR, player.rect, 1)
        lines = {
            -80: f"Wall Slide: {player.wall_sliding}",
            -60: f"State: {self.state}",
            -40: f"Jumps: {player.jump_count}/{MAX_JUMPS}",
            -20: f"On Ground: {player.on_ground}",
        }
        for dy, text in lines.items():
            rendered = self.debug_font.render(text, True, WHITE)
            surface.blit(rendered, (player.rect.x, player.rect.y + dy))


def _animation_state(player: Player) -> str:
    facing = "right" if player.facing_right else "left"
    if player.on_ground:
        action = "idle" if player.velocity_x == 0 else "run"
    elif player.wall_sliding:
        action = "wall_slide"
    elif player.velocity_y < 0:
        action = "jump"
    else:
        action = "fall"
    return f"{action}_{facing}"


class EnemySprites:
    def __init__(self) -> None:
        self.images = {enemy_type: _enemy_image(enemy_type) for enemy_type in EnemyType}
        self.projectile = pygame.Surface((10, 6))
        self.projectile.fill(PROJECTILE_COLOR)
        self.debug_font = pygame.font.SysFont(None, 20)

    def draw(self, surface: pygame.Surface, enemy: Enemy, offset: Offset) -> None:
        dx, dy = offset
        surface.blit(self.images[enemy.enemy_type], enemy.rect.move(dx, dy))
        for projectile in enemy.projectiles:
            surface.blit(self.projectile, projectile.rect.move(dx, dy))

        if DEBUG_MODE:
            y = enemy.rect.bottom + 5 + dy
            start = (enemy.start_x - enemy.patrol_distance + dx, y)
            end = (enemy.start_x + enemy.patrol_distance + dx, y)
            pygame.draw.line(surface, DEBUG_COLOR, start, end, 1)
            label = self.debug_font.render(enemy.enemy_type.value, True, WHITE)
            surface.blit(label, (enemy.rect.x + dx, enemy.rect.y - 20 + dy))


def _enemy_image(enemy_type: EnemyType) -> pygame.Surface:
    image = pygame.Surface((ENEMY_WIDTH, ENEMY_HEIGHT))
    if enemy_type is EnemyType.BASIC:
        image.fill(ENEMY_COLOR)
    elif enemy_type is EnemyType.JUMPER:
        image.fill((255, 100, 0))
        pygame.draw.polygon(
            image, (255, 200, 0), [(0, 0), (ENEMY_WIDTH, 0), (ENEMY_WIDTH // 2, -10)]
        )
    elif enemy_type is EnemyType.SHOOTER:
        image.fill((150, 0, 0))
        pygame.draw.circle(image, (255, 255, 0), (ENEMY_WIDTH // 2, ENEMY_HEIGHT // 2), 10)
    return image


class PlatformSprites:
    def __init__(self) -> None:
        self._cache: dict[tuple[int, int], pygame.Surface] = {}

    def draw(self, surface: pygame.Surface, platform: Platform, offset: Offset) -> None:
        size = platform.rect.size
        image = self._cache.get(size)
        if image is None:
            image = pygame.Surface(size)
            image.fill(PLATFORM_COLOR)
            self._cache[size] = image
        image.set_alpha(platform.alpha)
        surface.blit(image, platform.rect.move(offset))


class ExitSprite:
    def __init__(self, size: tuple[int, int]) -> None:
        self.image = pygame.Surface(size)
        self.timer = 0.0
        self._redraw()

    def advance(self) -> None:
        self.timer += EXIT_PULSE_STEP
        self._redraw()

    def _redraw(self) -> None:
        pulse = abs(math.sin(self.timer)) * 10
        self.image.fill(EXIT_COLOR)
        pygame.draw.ellipse(self.image, WHITE, (5, 5, 40, 70))
        inner = (10 + pulse / 4, 10 + pulse / 4, 30 - pulse / 2, 60 - pulse / 2)
        pygame.draw.ellipse(self.image, EXIT_COLOR, inner)

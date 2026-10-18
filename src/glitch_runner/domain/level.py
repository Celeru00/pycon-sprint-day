import random
from dataclasses import dataclass, field
from enum import Enum

from pygame import Rect

from glitch_runner.config import SHAKE_INTENSITY_LEVEL4, SHAKE_INTENSITY_LEVEL5
from glitch_runner.domain.enemy import Enemy, EnemyType
from glitch_runner.domain.platform import Platform
from glitch_runner.domain.player import Player

EXIT_WIDTH = 50
EXIT_HEIGHT = 80
DEFAULT_LIVES = 3
LEVEL_GLITCH_CHECK_FRAMES = 180
LEVEL_GLITCH_CHANCE = 0.3
LEVEL_GLITCH_MIN_FRAMES = 15
LEVEL_GLITCH_MAX_FRAMES = 45


@dataclass(frozen=True)
class EnemySpec:
    x: int
    y: int
    patrol_distance: int
    enemy_type: EnemyType


@dataclass(frozen=True)
class LevelSpec:
    name: str
    player_start: tuple[int, int]
    exit_pos: tuple[int, int]
    platforms: tuple[tuple[int, int, int, int], ...]
    enemies: tuple[EnemySpec, ...]
    lives: int = DEFAULT_LIVES
    shake_enabled: bool = False
    advanced_glitches: bool = False


class LevelGlitch(str, Enum):
    COLOR_SHIFT = "color_shift"
    STATIC = "static"


@dataclass
class LevelGlitchState:
    enabled: bool
    timer: int = 0
    effect: LevelGlitch | None = None
    remaining: int = 0

    def update(self) -> None:
        if not self.enabled:
            return
        self.timer += 1
        if (
            self.effect is None
            and self.timer >= LEVEL_GLITCH_CHECK_FRAMES
            and random.random() < LEVEL_GLITCH_CHANCE
        ):
            self.effect = random.choice(list(LevelGlitch))
            self.remaining = random.randint(LEVEL_GLITCH_MIN_FRAMES, LEVEL_GLITCH_MAX_FRAMES)
            self.timer = 0
        if self.effect is not None:
            self.remaining -= 1
            if self.remaining <= 0:
                self.effect = None


@dataclass
class ScreenShake:
    enabled: bool
    intensity: int
    offset: tuple[int, int] = field(default=(0, 0))

    def update(self) -> None:
        if self.enabled:
            self.offset = (
                random.randint(-self.intensity, self.intensity),
                random.randint(-self.intensity, self.intensity),
            )


class Level:
    def __init__(self, number: int, spec: LevelSpec) -> None:
        self.number = number
        self.spec = spec
        self.name = spec.name
        self.player_start = spec.player_start
        self.lives = spec.lives
        self.exit = Rect(*spec.exit_pos, EXIT_WIDTH, EXIT_HEIGHT)
        self.platforms = [Platform(*data) for data in spec.platforms]
        self.enemies = [Enemy(e.x, e.y, e.patrol_distance, e.enemy_type) for e in spec.enemies]
        intensity = SHAKE_INTENSITY_LEVEL4 if number == 4 else SHAKE_INTENSITY_LEVEL5
        self.shake = ScreenShake(spec.shake_enabled, intensity)
        self.glitch = LevelGlitchState(spec.advanced_glitches)

    @property
    def solid_platforms(self) -> list[Platform]:
        return [p for p in self.platforms if p.solid]

    def reset_player(self, player: Player, now: float) -> None:
        player.respawn(self.player_start, now)

    def update(self) -> None:
        self.shake.update()
        self.glitch.update()

    def update_enemies(self, player: Player) -> None:
        for enemy in self.enemies:
            enemy.update(self.platforms, player.rect)

    def player_reached_exit(self, player: Player) -> bool:
        return player.rect.colliderect(self.exit)

    def player_hit_enemy(self, player: Player) -> bool:
        if player.invincible:
            return False
        hit = False
        for enemy in self.enemies:
            if player.rect.colliderect(enemy.rect):
                hit = True
            if enemy.hit_by_projectile(player.rect):
                hit = True
            return hit

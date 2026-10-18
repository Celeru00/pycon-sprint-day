from collections.abc import Iterable
from enum import Enum

from pygame import Rect

from glitch_runner.config import (
    ENEMY_HEIGHT,
    ENEMY_SPEED,
    ENEMY_WIDTH,
    GRAVITY,
    JUMP_POWER,
    MAX_FALL_SPEED,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from glitch_runner.domain.platform import Platform

JUMP_INTERVAL_FRAMES = 120
JUMP_POWER_FACTOR = 0.7
SHOOT_INTERVAL_FRAMES = 180
SHOOT_VERTICAL_RANGE = 100
PROJECTILE_WIDTH = 10
PROJECTILE_HEIGHT = 6
PROJECTILE_SPEED = 7
COLLISION_TOLERANCE = 10


class EnemyType(str, Enum):
    BASIC = "basic"
    JUMPER = "jumper"
    SHOOTER = "shooter"


class Projectile:
    def __init__(self, x: int, y: int, direction: int) -> None:
        self.rect = Rect(x, y, PROJECTILE_WIDTH, PROJECTILE_HEIGHT)
        self.direction = direction

    def update(self) -> None:
        self.rect.x += PROJECTILE_SPEED * self.direction

    def is_off_screen(self) -> bool:
        return (
            self.rect.right < 0
            or self.rect.left > SCREEN_WIDTH
            or self.rect.bottom < 0
            or self.rect.top > SCREEN_HEIGHT
        )


class Enemy:
    def __init__(
        self,
        x: int,
        y: int,
        patrol_distance: int = 100,
        enemy_type: EnemyType = EnemyType.BASIC,
    ) -> None:
        self.enemy_type = EnemyType(enemy_type)
        self.rect = Rect(x, y, ENEMY_WIDTH, ENEMY_HEIGHT)
        self.velocity_x: float = ENEMY_SPEED
        self.velocity_y: float = 0
        self.direction = 1
        self.on_ground = False
        self.start_x = x
        self.patrol_distance = patrol_distance
        self.jump_timer = 0
        self.shoot_timer = 0
        self.projectiles: list[Projectile] = []

    def update(self, platforms: Iterable[Platform], target: Rect | None = None) -> None:
        self._apply_gravity()
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y
        self._resolve_collisions(platforms)
        self._patrol()

        if self.enemy_type is EnemyType.JUMPER and self.on_ground:
            self._update_jumping()
        elif self.enemy_type is EnemyType.SHOOTER and target is not None:
            self._update_shooting(target)

        self._update_projectiles()

    def hit_by_projectile(self, rect: Rect) -> bool:
        for projectile in self.projectiles:
            if rect.colliderect(projectile.rect):
                self.projectiles.remove(projectile)
                return True
        return False

    def _apply_gravity(self) -> None:
        if not self.on_ground:
            self.velocity_y = min(self.velocity_y + GRAVITY, MAX_FALL_SPEED)

    def _turn_around(self) -> None:
        self.direction *= -1
        self.velocity_x = ENEMY_SPEED * self.direction

    def _resolve_collisions(self, platforms: Iterable[Platform]) -> None:
        self.on_ground = False
        for platform in platforms:
            wall = platform.rect
            if not (platform.solid and self.rect.colliderect(wall)):
                continue
            if (
                self.velocity_y > 0
                and self.rect.bottom - self.velocity_y <= wall.top + COLLISION_TOLERANCE
            ):
                self.rect.bottom = wall.top
                self.velocity_y = 0
                self.on_ground = True
            elif (
                self.velocity_y < 0
                and self.rect.top - self.velocity_y >= wall.bottom - COLLISION_TOLERANCE
            ):
                self.rect.top = wall.bottom
                self.velocity_y = 0
            elif self.velocity_x > 0:
                self.rect.right = wall.left
                self._turn_around()
            elif self.velocity_x < 0:
                self.rect.left = wall.right
                self._turn_around()

    def _patrol(self) -> None:
        if self.rect.x > self.start_x + self.patrol_distance:
            self.direction = -1
            self.velocity_x = ENEMY_SPEED * self.direction
        elif self.rect.x < self.start_x + self.patrol_distance:
            self.direction = 1
            self.velocity_x = ENEMY_SPEED * self.direction

    def _update_jumping(self) -> None:
        self.jump_timer += 1
        if self.jump_timer >= JUMP_INTERVAL_FRAMES:
            self.velocity_y = -JUMP_POWER * JUMP_POWER_FACTOR
            self.jump_timer = 0

    def _update_shooting(self, target: Rect) -> None:
        self.shoot_timer += 1
        if self.shoot_timer < SHOOT_INTERVAL_FRAMES:
            return
        if abs(target.y - self.rect.y) < SHOOT_VERTICAL_RANGE:
            direction = -1 if target.x > self.rect.x else 1
            self.projectiles.append(Projectile(self.rect.centerx, self.rect.centery, direction))
            self.shoot_timer = 0

    def _update_projectiles(self) -> None:
        for projectile in self.projectiles:
            projectile.update()
        self.projectiles = [p for p in self.projectiles if not p.is_off_screen()]

from collections.abc import Sequence

from pygame import Rect

from glitch_runner.config import (
    GRAVITY,
    JUMP_POWER,
    MAX_FALL_SPEED,
    PLAYER_HEIGHT,
    PLAYER_SPEED,
    PLAYER_WIDTH,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from glitch_runner.domain.input import HeldKeys, PlayerCommand
from glitch_runner.domain.platform import Platform

MAX_JUMPS = 2
MAX_JUMP_TIME = 15
JUMP_HOLD_BOOST = 0.5
INVINCIBLE_DURATION = 2
WALL_SLIDE_SPEED = 1
WALL_JUMP_POWER = 10
WALL_SLIDE_GRAVITY_FACTOR = 0.5
COLLISION_TOLERANCE = 10


class Player:
    def __init__(self, width: int = PLAYER_WIDTH, height: int = PLAYER_HEIGHT) -> None:
        self.rect = Rect(100, SCREEN_HEIGHT - PLAYER_HEIGHT - 100, width, height)
        self.velocity_x: float = 0
        self.velocity_y: float = 0
        self.on_ground = False
        self.facing_right = True

        self.jump_count = 0
        self.jump_held = False
        self.jump_time = 0
        self.wall_sliding = False

        self.invincible = False
        self.invincible_since = 0.0

        self.gravity = GRAVITY
        self.ceiling_enabled = False
        self.speed: float = PLAYER_SPEED
        self.jump_power = JUMP_POWER

    def respawn(self, position: tuple[int, int], now: float) -> None:
        self.rect.x, self.rect.y = position
        self.velocity_x = 0
        self.velocity_y = 0
        self.set_invincible(now)

    def set_invincible(self, now: float) -> None:
        self.invincible = True
        self.invincible_since = now

    def handle_command(self, command: PlayerCommand) -> bool:
        if command is PlayerCommand.PRESS_LEFT:
            self.velocity_x = -self.speed
            self.facing_right = False
        elif command is PlayerCommand.PRESS_RIGHT:
            self.velocity_x = self.speed
            self.facing_right = True
        elif command is PlayerCommand.PRESS_JUMP:
            return self._press_jump()
        elif command is PlayerCommand.RELEASE_LEFT:
            self._stop_moving(direction=-1)
        elif command is PlayerCommand.RELEASE_RIGHT:
            self._stop_moving(direction=1)
        elif command is PlayerCommand.RELEASE_JUMP:
            self.jump_held = False
        return False

    def _stop_moving(self, direction: int) -> None:
        if self.velocity_x * direction > 0:
            self.velocity_x = 0

    def update(self, platforms: Sequence[Platform], held: HeldKeys, now: float) -> None:
        self._apply_held_keys(held)

        if self.invincible and now - self.invincible_since > INVINCIBLE_DURATION:
            self.invincible = False

        self._apply_gravity()
        if platforms:
            self._check_wall_slide(platforms)

        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y

        if platforms:
            self._resolve_collisions(platforms)
        self._clamp_to_screen()

    def _apply_held_keys(self, held: HeldKeys) -> None:
        if held.left:
            self.velocity_x = -self.speed
            self.facing_right = False
        elif held.right:
            self.velocity_x = self.speed
            self.facing_right = True
        else:
            self.velocity_x = 0

        if held.jump and self.jump_held and self.jump_time < MAX_JUMP_TIME and self.velocity_y < 0:
            self.velocity_y -= JUMP_HOLD_BOOST
            self.jump_time += 1

    def _press_jump(self) -> bool:
        if self.on_ground:
            self._jump()
            self.jump_count = 1
        elif self.wall_sliding:
            self._wall_jump()
        elif self.jump_count < MAX_JUMPS:
            self._jump()
            self.jump_count += 1
        else:
            return False
        self.jump_held = True
        self.jump_time = 0
        return True

    def _jump(self) -> None:
        self.velocity_y = -self.jump_power
        self.on_ground = False
        self.wall_sliding = False

    def _wall_jump(self) -> None:
        self.velocity_x = -WALL_JUMP_POWER if self.facing_right else WALL_JUMP_POWER
        self.velocity_y = -self.jump_power
        self.wall_sliding = False
        self.on_ground = False

    def _apply_gravity(self) -> None:
        if self.on_ground:
            return
        if self.wall_sliding:
            self.velocity_y += self.gravity * WALL_SLIDE_GRAVITY_FACTOR
            self.velocity_y = min(self.velocity_y, WALL_SLIDE_SPEED)
        else:
            self.velocity_y += self.gravity
            self.velocity_y = min(self.velocity_y, MAX_FALL_SPEED)

    def _check_wall_slide(self, platforms: Sequence[Platform]) -> None:
        if self.on_ground or self.velocity_y <= 0:
            return

        probe = self.rect.inflate(4, 0)
        for platform in platforms:
            wall = platform.rect
            overlaps_vertically = probe.bottom > wall.top and probe.top < wall.bottom
            if not overlaps_vertically:
                continue
            if self.velocity_x < 0 and probe.left <= wall.right < probe.right:
                self.wall_sliding = True
                self.facing_right = True
                return
            if self.velocity_x > 0 and probe.left < wall.left <= probe.right:
                self.wall_sliding = True
                self.facing_right = False
                return

        self.wall_sliding = False

    def _resolve_collisions(self, platforms: Sequence[Platform]) -> None:
        self.on_ground = False
        for platform in platforms:
            wall = platform.rect
            if not self.rect.colliderect(wall):
                continue
            if (
                self.velocity_y > 0
                and self.rect.bottom - self.velocity_y <= wall.top + COLLISION_TOLERANCE
            ):
                self.rect.bottom = wall.top
                self.velocity_y = 0
                self.on_ground = True
                self.jump_count = 0
            elif (
                self.velocity_y < 0
                and self.rect.top - self.velocity_y >= wall.bottom - COLLISION_TOLERANCE
            ):
                self.rect.top = wall.bottom
                self.velocity_y = 0
            elif (
                self.velocity_x > 0
                and self.rect.right - self.velocity_x <= wall.left + COLLISION_TOLERANCE
            ):
                self.rect.right = wall.left
                self.velocity_x = 0
            elif (
                self.velocity_x < 0
                and self.rect.left - self.velocity_x >= wall.right - COLLISION_TOLERANCE
            ):
                self.rect.left = wall.right
                self.velocity_x = 0

    def _clamp_to_screen(self) -> None:
        falling_in_air = self.velocity_y > 0 and not self.on_ground
        if self.rect.left < 0:
            self.rect.left = 0
            if falling_in_air:
                self.wall_sliding = True
                self.facing_right = True
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            if falling_in_air:
                self.wall_sliding = True
                self.facing_right = False
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.velocity_y = 0
            self.on_ground = True
            self.jump_count = 0
        if self.ceiling_enabled and self.rect.top < 0:
            self.rect.top = 0
            self.velocity_y = 0

import random
from dataclasses import dataclass, field
from enum import Enum

from glitch_runner.config import (
    FPS,
    GLITCH_DURATION,
    GLITCH_INTERVAL,
    GLITCH_NOTIFICATION_TIME,
    GRAVITY,
    PLAYER_SPEED,
    SCREEN_HEIGHT,
)
from glitch_runner.domain.input import PlayerCommand
from glitch_runner.domain.level import Level
from glitch_runner.domain.platform import Platform
from glitch_runner.domain.player import Player

FLICKER_PERIOD_FRAMES = 5
PLATFORM_FADE_STEP = 5
PLATFORM_SAFE_ZONE = 100
PIXEL_SIZES = (2, 3, 4, 6, 8)


class GlitchKind(str, Enum):
    REVERSED_GRAVITY = "reversed_gravity"
    FLICKERING_SPRITES = "flickering_sprites"
    INPUT_LAG = "input_lag"
    COLOR_DISTORTION = "color_distortion"
    SCREEN_SHAKE = "screen_shake"
    PLATFORM_DISAPPEAR = "platform_disappear"
    SPEED_CHANGE = "speed_change"
    PIXELATION = "pixelation"

    @property
    def label(self) -> str:
        return self.value.replace("_", "").upper()


@dataclass
class ScreenEffects:
    visible: bool = True
    color_shift: tuple[int, int, int] = (0, 0, 0)
    shake_amount: int = 0
    offset: tuple[int, int] = (0, 0)
    pixel_size: int = 1


@dataclass
class ActiveGlitch:
    kind: GlitchKind
    started_at: float


@dataclass
class _BufferedCommand:
    received_at: float
    command: PlayerCommand


@dataclass
class GlitchEngine:
    last_glitch_time: float
    interval: float = GLITCH_INTERVAL
    duration: float = GLITCH_DURATION
    kinds: tuple[GlitchKind, ...] = tuple(GlitchKind)
    active: list[ActiveGlitch] = field(default_factory=list)
    screen: ScreenEffects = field(default_factory=ScreenEffects)
    notification_text: str = ""
    notification_time: float = 0.0
    input_lag_frames: int = 0
    speed_multiplier: float = 1.0
    _flicker_timer: int = 0
    _input_buffer: list[_BufferedCommand] = field(default_factory=list)
    _disappearing: list[Platform] = field(default_factory=list)

    @property
    def active_labels(self) -> list[str]:
        return [glitch.kind.label for glitch in self.active]

    def notification(self, now: float) -> str | None:
        if self.notification_text and now - self.notification_time < GLITCH_NOTIFICATION_TIME:
            return self.notification_text
        return None

    def update(self, now: float, player: Player, level: Level) -> GlitchKind | None:
        triggered = None
        if now - self.last_glitch_time > self.interval:
            triggered = self._trigger(random.choice(self.kinds), now, player, level)
            self.last_glitch_time = now

        for glitch in list(self.active):
            if now - glitch.started_at > self.duration:
                self._deactivate(glitch.kind, player)
                self.active.remove(glitch)
            else:
                self._tick(glitch.kind)
        return triggered

    def process_command(self, command: PlayerCommand, now: float) -> PlayerCommand | None:
        if self.input_lag_frames > 0:
            self._input_buffer.append(_BufferedCommand(now, command))
            return None
        return command

    def release_lagged_commands(self, now: float) -> list[PlayerCommand]:
        delay = self.input_lag_frames / FPS
        ready: list[PlayerCommand] = []
        pending: list[_BufferedCommand] = []
        for buffered in self._input_buffer:
            if now - buffered.received_at >= delay:
                ready.append(buffered.command)
            else:
                pending.append(buffered)
        self._input_buffer = pending
        return ready

    def _trigger(self, kind: GlitchKind, now: float, player: Player, level: Level) -> GlitchKind:
        self._activate(kind, player, level)
        self.active.append(ActiveGlitch(kind, now))
        self.notification_text = f"GLITCH: {kind.label}"
        self.notification_time = now
        return kind

    def _activate(self, kind: GlitchKind, player: Player, level: Level) -> None:
        if kind is GlitchKind.REVERSED_GRAVITY:
            player.velocity_y = -player.velocity_y
            player.gravity = -GRAVITY
            player.ceiling_enabled = True
        elif kind is GlitchKind.FLICKERING_SPRITES:
            self._flicker_timer = 0
            self.screen.visible = True
        elif kind is GlitchKind.INPUT_LAG:
            self.input_lag_frames = random.randint(5, 15)
            self._input_buffer = []
        elif kind is GlitchKind.COLOR_DISTORTION:
            self.screen.color_shift = (
                random.randint(-100, 100),
                random.randint(-100, 100),
                random.randint(-100, 100),
            )
        elif kind is GlitchKind.SCREEN_SHAKE:
            self.screen.shake_amount = random.randint(5, 15)
        elif kind is GlitchKind.PLATFORM_DISAPPEAR:
            self._start_platform_disappear(level)
        elif kind is GlitchKind.SPEED_CHANGE:
            self.speed_multiplier = random.uniform(0.5, 2.0)
            player.speed = PLAYER_SPEED * self.speed_multiplier
        elif kind is GlitchKind.PIXELATION:
            self.screen.pixel_size = random.choice(PIXEL_SIZES)

    def _deactivate(self, kind: GlitchKind, player: Player) -> None:
        if kind is GlitchKind.REVERSED_GRAVITY:
            player.velocity_y = -player.velocity_y
            player.gravity = GRAVITY
            player.ceiling_enabled = False
        elif kind is GlitchKind.FLICKERING_SPRITES:
            self.screen.visible = True
        elif kind is GlitchKind.INPUT_LAG:
            self.input_lag_frames = 0
            self._input_buffer = []
        elif kind is GlitchKind.COLOR_DISTORTION:
            self.screen.color_shift = (0, 0, 0)
        elif kind is GlitchKind.SCREEN_SHAKE:
            self.screen.shake_amount = 0
            self.screen.offset = (0, 0)
        elif kind is GlitchKind.PLATFORM_DISAPPEAR:
            for platform in self._disappearing:
                platform.restore()
            self._disappearing = []
        elif kind is GlitchKind.SPEED_CHANGE:
            player.speed = PLAYER_SPEED
            self.speed_multiplier = 1.0
        elif kind is GlitchKind.PIXELATION:
            self.screen.pixel_size = 1

    def _tick(self, kind: GlitchKind) -> None:
        if kind is GlitchKind.FLICKERING_SPRITES:
            self._flicker_timer += 1
            if self._flicker_timer >= FLICKER_PERIOD_FRAMES:
                self.screen.visible = not self.screen.visible
                self._flicker_timer = 0
        elif kind is GlitchKind.SCREEN_SHAKE and self.screen.shake_amount > 0:
            amount = self.screen.shake_amount
            self.screen.offset = (random.randint(-amount, amount), random.randint(-amount, amount))
        elif kind is GlitchKind.PLATFORM_DISAPPEAR:
            for platform in self._disappearing:
                platform.fade(PLATFORM_FADE_STEP)

    def _start_platform_disappear(self, level: Level) -> None:
        candidates = [p for p in level.platforms if p.rect.y > SCREEN_HEIGHT - PLATFORM_SAFE_ZONE]
        if not candidates:
            return
        count = min(len(candidates), random.randint(1, 3))
        self._disappearing = random.sample(candidates, count)
        for platform in self._disappearing:
            platform.start_disappearing()

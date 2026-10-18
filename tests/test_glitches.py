from glitch_runner.config import GRAVITY, PLAYER_SPEED
from glitch_runner.domain.glitches import GlitchEngine, GlitchKind
from glitch_runner.domain.input import PlayerCommand
from glitch_runner.domain.level import Level
from glitch_runner.domain.levels import LEVEL_2
from glitch_runner.domain.player import Player


def trigger(kind: GlitchKind, engine: GlitchEngine, player: Player, level: Level) -> None:
    engine._trigger(kind, 0.0, player, level)


def test_glitch_triggers_after_interval_and_expires():
    engine = GlitchEngine(last_glitch_time=0.0, kinds=(GlitchKind.PIXELATION,))
    player, level = Player(), Level(2, LEVEL_2)

    assert engine.update(5.0, player, level) is None
    assert engine.update(10.5, player, level) is GlitchKind.PIXELATION
    assert engine.screen.pixel_size > 1
    assert engine.active_labels == ["PIXELATION"]
    assert engine.notification(11.0) == "GLITCH: PIXELATION"

    engine.update(16.0, player, level)
    assert engine.active == []
    assert engine.screen.pixel_size == 1


def test_reversed_gravity_is_restored():
    engine, player, level = GlitchEngine(0.0), Player(), Level(2, LEVEL_2)
    trigger(GlitchKind.REVERSED_GRAVITY, engine, player, level)
    assert player.gravity == -GRAVITY
    assert player.ceiling_enabled
    engine._deactivate(GlitchKind.REVERSED_GRAVITY, player)
    assert player.gravity == GRAVITY
    assert not player.ceiling_enabled


def test_speed_change_is_restored():
    engine, player, level = GlitchEngine(0.0), Player(), Level(2, LEVEL_2)
    trigger(GlitchKind.SPEED_CHANGE, engine, player, level)
    assert player.speed == PLAYER_SPEED * engine.speed_multiplier
    engine._deactivate(GlitchKind.SPEED_CHANGE, player)
    assert player.speed == PLAYER_SPEED


def test_input_lag_buffers_commands_until_delay_passes():
    engine, player, level = GlitchEngine(0.0), Player(), Level(2, LEVEL_2)
    trigger(GlitchKind.INPUT_LAG, engine, player, level)
    assert engine.process_command(PlayerCommand.PRESS_JUMP, now=1.0) is None
    assert engine.release_lagged_commands(now=1.0) == []
    assert engine.release_lagged_commands(now=2.0) == [PlayerCommand.PRESS_JUMP]


def test_disappearing_platforms_fade_out_and_come_back():
    engine, player, level = GlitchEngine(0.0), Player(), Level(2, LEVEL_2)
    trigger(GlitchKind.PLATFORM_DISAPPEAR, engine, player, level)
    fading = [p for p in level.platforms if p.disappearing]
    assert 1 <= len(fading) <= 3

    for _ in range(60):
        engine._tick(GlitchKind.PLATFORM_DISAPPEAR)
    assert all(not p.solid and p.alpha == 0 for p in fading)

    engine._deactivate(GlitchKind.PLATFORM_DISAPPEAR, player)
    assert all(p.solid and p.alpha == 255 for p in fading)

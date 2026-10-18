from glitch_runner.config import GRAVITY, JUMP_POWER, SCREEN_HEIGHT
from glitch_runner.domain.input import HeldKeys, PlayerCommand
from glitch_runner.domain.platform import Platform
from glitch_runner.domain.player import Player

NO_KEYS = HeldKeys()


def landed_player() -> tuple[Player, list[Platform]]:
    ground = [Platform(0, SCREEN_HEIGHT - 50, 800, 50)]
    player = Player()
    player.rect.bottom = ground[0].rect.top
    player.on_ground = True
    return player, ground


def test_gravity_pulls_player_down_when_airborne():
    player = Player()
    start_y = player.rect.y
    player.update([], NO_KEYS, now=0)
    assert player.velocity_y == GRAVITY
    assert player.rect.y >= start_y


def test_player_lands_on_platform():
    player, ground = landed_player()
    player.on_ground = False
    player.rect.bottom = ground[0].rect.top - 1
    landed = False
    for _ in range(10):
        player.update(ground, NO_KEYS, now=0)
        landed = landed or player.on_ground
    assert landed
    assert player.rect.bottom == ground[0].rect.top
    assert player.jump_count == 0


def test_jump_then_double_jump_then_no_more():
    player, _ = landed_player()
    assert player.handle_command(PlayerCommand.PRESS_JUMP)
    assert player.velocity_y == -JUMP_POWER
    assert player.handle_command(PlayerCommand.PRESS_JUMP)
    assert player.jump_count == 2
    assert not player.handle_command(PlayerCommand.PRESS_JUMP)


def test_held_keys_drive_horizontal_velocity():
    player, ground = landed_player()
    player.update(ground, HeldKeys(right=True), now=0)
    assert player.velocity_x == player.speed
    assert player.facing_right
    player.update(ground, HeldKeys(left=True), now=0)
    assert player.velocity_x == -player.speed
    assert not player.facing_right


def test_release_only_stops_matching_direction():
    player = Player()
    player.velocity_x = 5
    player.handle_command(PlayerCommand.RELEASE_LEFT)
    assert player.velocity_x == 5
    player.handle_command(PlayerCommand.RELEASE_RIGHT)
    assert player.velocity_x == 0


def test_invincibility_expires_after_two_seconds():
    player, ground = landed_player()
    player.set_invincible(now=10)
    player.update(ground, NO_KEYS, now=11)
    assert player.invincible
    player.update(ground, NO_KEYS, now=12.1)
    assert not player.invincible

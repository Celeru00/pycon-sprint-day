from glitch_runner.application.ports import Sound
from glitch_runner.application.session import GameState
from glitch_runner.domain.input import HeldKeys, PlayerCommand
from glitch_runner.domain.levels import LEVELS


def start(session):
    session.confirm()
    assert session.state is GameState.PLAYING


def test_starting_sets_lives_and_respawns_player(session, audio):
    start(session)
    assert session.lives == LEVELS[0].lives
    assert session.max_lives == LEVELS[0].lives
    assert (session.player.rect.x, session.player.rect.y) == LEVELS[0].player_start
    assert session.player.invincible
    assert audio.played == [Sound.LEVEL_COMPLETE]


def test_reaching_exit_scores_and_advances(session, clock):
    start(session)
    clock.advance(10)
    session.player.rect.center = session.current_level.exit.center
    session.update(HeldKeys())
    assert session.state is GameState.LEVEL_COMPLETE
    assert session.score == 1000 + (60 - 10) * 10

    clock.advance(2.5)
    session.update(HeldKeys())
    assert session.state is GameState.PLAYING
    assert session.level_index == 1
    assert session.lives == LEVELS[1].lives


def test_touching_enemy_costs_a_life_then_respawns(session, clock, audio):
    start(session)
    session.player.invincible = False
    enemy = session.current_level.enemies[0]
    session.player.rect.center = enemy.rect.center
    session.update(HeldKeys())
    assert session.state is GameState.GAME_OVER
    assert session.lives == LEVELS[0].lives - 1
    assert audio.played[-1] is Sound.GAME_OVER

    clock.advance(2.5)
    session.update(HeldKeys())
    assert session.state is GameState.PLAYING
    assert session.lives == LEVELS[0].lives - 1


def test_losing_last_life_waits_for_confirm_then_returns_to_menu(session, audio):
    start(session)
    session.lives = 1
    session._lose_life()
    assert audio.played[-1] is Sound.FINAL_DEATH
    session.update(HeldKeys())
    assert session.state is GameState.GAME_OVER

    session.confirm()
    assert session.state is GameState.MENU
    assert session.score == 0
    assert session.level_index == 0


def test_completing_last_level_finishes_game(session, audio):
    start(session)
    session.level_index = len(LEVELS) - 1
    session.state = GameState.LEVEL_COMPLETE
    session.confirm()
    assert session.state is GameState.GAME_COMPLETED
    assert audio.played[-1] is Sound.GAME_COMPLETED


def test_jump_command_plays_jump_sound(session, audio):
    start(session)
    session.player.on_ground = True
    session.handle_command(PlayerCommand.PRESS_JUMP)
    assert audio.played[-1] is Sound.JUMP


def test_commands_ignored_outside_play(session):
    session.handle_command(PlayerCommand.PRESS_RIGHT)
    assert session.player.velocity_x == 0


def test_toggle_music(session):
    session.toggle_music()
    assert session.music_muted

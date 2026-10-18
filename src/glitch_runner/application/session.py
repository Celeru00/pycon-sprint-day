from collections.abc import Sequence
from enum import Enum, auto

from glitch_runner.application.ports import AudioPort, Clock, Sound
from glitch_runner.config import SCREEN_HEIGHT
from glitch_runner.domain.glitches import GlitchEngine
from glitch_runner.domain.input import HeldKeys, PlayerCommand
from glitch_runner.domain.level import Level, LevelSpec
from glitch_runner.domain.player import Player

LEVEL_COMPLETE_SCORE = 1000
TIME_BONUS_WINDOW = 60
TIME_BONUS_PER_SECOND = 10
TRANSITION_DELAY = 2


class GameState(Enum):
    MENU = auto()
    PLAYING = auto()
    GAME_OVER = auto()
    LEVEL_COMPLETE = auto()
    GAME_COMPLETED = auto()


class GameSession:
    def __init__(
        self,
        level_specs: Sequence[LevelSpec],
        player: Player,
        audio: AudioPort,
        clock: Clock,
    ) -> None:
        self.audio = audio
        self.clock = clock
        self.player = player
        self.levels = [Level(number, spec) for number, spec in enumerate(level_specs, start=1)]
        self.glitches = GlitchEngine(last_glitch_time=clock.now())

        self.state = GameState.MENU
        self.level_index = 0
        self.current_level = self.levels[0]
        self.lives = 0
        self.max_lives = 0
        self.score = 0
        self.level_start_time = 0.0
        self.game_over_time = 0.0
        self.level_complete_time = 0.0

    @property
    def music_muted(self) -> bool:
        return self.audio.music_muted

    def toggle_music(self) -> None:
        self.audio.toggle_music_mute()

    def confirm(self) -> None:
        if self.state is GameState.MENU:
            self.state = GameState.PLAYING
            self._reset_level(reset_lives=True)
            self.audio.play_sound(Sound.LEVEL_COMPLETE)
        elif self.state is GameState.GAME_OVER:
            if self.lives > 0:
                self.state = GameState.PLAYING
                self._reset_level(reset_lives=False)
            else:
                self._return_to_menu()
        elif self.state is GameState.LEVEL_COMPLETE:
            self._next_level()
        elif self.state is GameState.GAME_COMPLETED:
            self._return_to_menu()

    def handle_command(self, command: PlayerCommand) -> None:
        if self.state is not GameState.PLAYING:
            return
        processed = self.glitches.process_command(command, self.clock.now())
        if processed is not None:
            self._apply_player_command(processed)

    def release_lagged_commands(self) -> None:
        if self.state is not GameState.PLAYING:
            return
        for command in self.glitches.release_lagged_commands(self.clock.now()):
            self._apply_player_command(command)

    def update(self, held: HeldKeys) -> None:
        if self.state is GameState.PLAYING:
            self._update_playing(held)

        now = self.clock.now()
        if (
            self.state is GameState.GAME_OVER
            and now - self.game_over_time > TRANSITION_DELAY
            and self.lives > 0
        ):
            self.state = GameState.PLAYING
            self._reset_level(reset_lives=False)

        if (
            self.state is GameState.LEVEL_COMPLETE
            and now - self.level_complete_time > TRANSITION_DELAY
        ):
            self._next_level()

    def _update_playing(self, held: HeldKeys) -> None:
        if self.glitches.update(self.clock.now(), self.player, self.current_level):
            self.audio.play_sound(Sound.GLITCH)

        level = self.current_level
        level.update()
        level.update_enemies(self.player)
        self.player.update(level.solid_platforms, held, self.clock.now())

        if level.player_reached_exit(self.player):
            self._complete_level()
        if level.player_hit_enemy(self.player):
            self._lose_life()
        if self.player.rect.top > SCREEN_HEIGHT:
            self._lose_life()

    def _apply_player_command(self, command: PlayerCommand) -> None:
        if self.player.handle_command(command):
            self.audio.play_sound(Sound.JUMP)

    def _complete_level(self) -> None:
        now = self.clock.now()
        self.state = GameState.LEVEL_COMPLETE
        self.level_complete_time = now
        self.score = LEVEL_COMPLETE_SCORE
        self.audio.play_sound(Sound.LEVEL_COMPLETE)
        elapsed = int(now - self.level_start_time)
        self.score += (TIME_BONUS_WINDOW - elapsed) * TIME_BONUS_PER_SECOND

    def _lose_life(self) -> None:
        self.lives -= 1
        self.state = GameState.GAME_OVER
        self.game_over_time = self.clock.now()
        self.audio.play_sound(Sound.FINAL_DEATH if self.lives <= 0 else Sound.GAME_OVER)

    def _reset_level(self, reset_lives: bool) -> None:
        now = self.clock.now()
        self.current_level.reset_player(self.player, now)
        self.level_start_time = now
        if reset_lives:
            self.max_lives = self.current_level.lives
            self.lives = self.max_lives

    def _next_level(self) -> None:
        self.level_index += 1
        if self.level_index < len(self.levels) - 1:
            self.current_level = self.levels[self.level_index]
            self._reset_level(reset_lives=True)
            self.state = GameState.PLAYING
        else:
            self.state = GameState.GAME_COMPLETED
            self.audio.play_sound(Sound.GAME_COMPLETED)

    def _return_to_menu(self) -> None:
        self.state = GameState.MENU
        self.score = 0
        self.level_index = 0
        self.current_level = self.levels[0]
        self._reset_level(reset_lives=True)

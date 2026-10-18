from enum import Enum
from typing import Protocol


class Sound(str, Enum):
    JUMP = "jump"
    LAND = "land"
    GLITCH = "glitch"
    LEVEL_COMPLETE = "level_complete"
    GAME_OVER = "game_over"
    FINAL_DEATH = "final_death"
    GAME_COMPLETED = "game_completed"


class AudioPort(Protocol):
    @property
    def music_muted(self) -> bool: ...

    def play_sound(self, sound: Sound) -> None: ...

    def play_music(self, name: str) -> None: ...

    def toggle_music_mute(self) -> None: ...


class Clock(Protocol):
    def now(self) -> float: ...

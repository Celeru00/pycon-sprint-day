import pytest

from glitch_runner.application.ports import Sound
from glitch_runner.application.session import GameSession
from glitch_runner.domain.levels import LEVELS
from glitch_runner.domain.player import Player


class FakeClock:
    def __init__(self, start: float = 1000.0) -> None:
        self.time = start

    def now(self) -> float:
        return self.time

    def advance(self, seconds: float) -> None:
        self.time += seconds


class FakeAudio:
    def __init__(self) -> None:
        self.played: list[Sound] = []
        self.music_muted = False

    def play_sound(self, sound: Sound) -> None:
        self.played.append(sound)

    def play_music(self, name: str) -> None:
        pass

    def toggle_music_mute(self) -> None:
        self.music_muted = not self.music_muted


@pytest.fixture
def clock() -> FakeClock:
    return FakeClock()


@pytest.fixture
def audio() -> FakeAudio:
    return FakeAudio()


@pytest.fixture
def session(clock: FakeClock, audio: FakeAudio) -> GameSession:
    return GameSession(LEVELS, Player(), audio, clock)

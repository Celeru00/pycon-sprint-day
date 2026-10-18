import io
import logging
import math
import wave
from array import array

import pygame  # type: ignore[import-not-found]

from glitch_runner.application.ports import Sound
from glitch_runner.config import DEFAULT_MUSIC_VOLUME, DEFAULT_SFX_VOLUME
from glitch_runner.infrastructure.resources import SOUNDS_DIR, first_existing

logger = logging.getLogger(__name__)

SOUND_FILES: dict[Sound, tuple[str, ...]] = {
    Sound.JUMP: ("jump.wav", "jump-audio.mp3", "jump.mp3"),
    Sound.LAND: ("land.wav",),
    Sound.GLITCH: ("glitch.wav", "glitch.mp3"),
    Sound.LEVEL_COMPLETE: ("level_complete.wav", "level_complete.mp3"),
    Sound.GAME_OVER: ("pixel-explosion-319166.mp3", "game-over.mp3", "death.mp3", "death.wav"),
    Sound.FINAL_DEATH: ("pixel-death-66829.mp3", "final-death.mp3", "final-death.wav"),
    Sound.GAME_COMPLETED: ("good-result-82807.mp3", "complete.mp3", "complete.wav", "game_completed.mp3"),
}

PLACEHOLDER_SAMPLE_RATE = 44100
PLACEHOLDER_FREQUENCY = 440
PLACEHOLDER_VOLUME = 0.5
PLACEHOLDER_MUSIC_VOLUME_FACTOR = 0.5


class PygameAudio:
    def __init__(
        self,
        music_volume: float = DEFAULT_MUSIC_VOLUME,
        sfx_volume: float = DEFAULT_SFX_VOLUME,
    ) -> None:
        pygame.mixer.init()
        self.music_volume = music_volume
        self.sfx_volume = sfx_volume
        self._muted = False
        self._sounds = self._load_sounds()

    @property
    def music_muted(self) -> bool:
        return self._muted

    def play_sound(self, sound: Sound) -> None:
        effect = self._sounds.get(sound)
        if effect is not None:
            effect.play()

    def play_music(self, name: str) -> None:
        path = SOUNDS_DIR / f"{name}.mp3"
        try:
            if path.exists():
                pygame.mixer.music.load(path)
                self._start_music(self.music_volume)
            else:
                pygame.mixer.music.load(_placeholder_tone())
                self._start_music(self.music_volume * PLACEHOLDER_MUSIC_VOLUME_FACTOR)
        except pygame.error:
            logger.exception("Could not play music %s", name)

    def toggle_music_mute(self) -> None:
        self._muted = not self._muted
        pygame.mixer.music.set_volume(0 if self._muted else self.music_volume)

    def _start_music(self, volume: float) -> None:
        pygame.mixer.music.set_volume(0 if self._muted else volume)
        pygame.mixer.music.play(-1)

    def _load_sounds(self) -> dict[Sound, pygame.mixer.Sound]:
        sounds: dict[Sound, pygame.mixer.Sound] = {}
        for sound, filenames in SOUND_FILES.items():
            path = first_existing([SOUNDS_DIR / name for name in filenames])
            if path is None:
                logger.info("No sound file found for %s", sound.value)
                continue
            try:
                effect = pygame.mixer.Sound(path)
            except pygame.error:
                logger.exception("Failed to load %s from %s", sound.value, path)
                continue
            effect.set_volume(self.sfx_volume)
            sounds[sound] = effect
        return sounds


def _placeholder_tone() -> io.BytesIO:
    samples = array(
        "h",
        (
            int(
                PLACEHOLDER_VOLUME
                * 32767
                * math.sin(2 * math.pi * PLACEHOLDER_FREQUENCY * i / PLACEHOLDER_SAMPLE_RATE)
            )
            for i in range(PLACEHOLDER_SAMPLE_RATE)
        ),
    )
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(PLACEHOLDER_SAMPLE_RATE)
        wav.writeframes(samples.tobytes())
    buffer.seek(0)
    return buffer

import logging

import pygame

from glitch_runner.application.session import GameSession, GameState
from glitch_runner.config import FPS, SCREEN_HEIGHT, SCREEN_WIDTH, TITLE, VERSION
from glitch_runner.domain.levels import LEVELS
from glitch_runner.domain.player import Player
from glitch_runner.infrastructure.audio import PygameAudio
from glitch_runner.infrastructure.clock import SystemClock
from glitch_runner.infrastructure.images import load_background, load_player_sprites
from glitch_runner.presentation.input import SystemAction, held_keys, translate
from glitch_runner.presentation.renderer import GameRenderer


class GlitchRunnerApp:
    def __init__(self) -> None:
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(f"{TITLE} {VERSION}")
        self.frame_clock = pygame.time.Clock()

        frames = load_player_sprites()
        width, height = frames["idle_right"][0].get_size()
        self.audio = PygameAudio()
        clock = SystemClock()
        self.session = GameSession(LEVELS, Player(width, height), self.audio, clock)
        self.renderer = GameRenderer(
            self.screen,
            frames,
            self.session.levels,
            clock,
            self.frame_clock,
            load_background,
        )
        self.running = True

    def run(self) -> None:
        self.audio.play_music("background")
        while self.running:
            self._handle_events()
            was_playing = self.session.state is GameState.PLAYING
            self.session.update(held_keys())
            if was_playing:
                self.renderer.advance(self.session)
            self.renderer.render(self.session)
            self.frame_clock.tick(FPS)

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            translated = translate(event)
            if translated is None:
                continue
            if translated.action is SystemAction.QUIT:
                self.running = False
            elif translated.action is SystemAction.TOGGLE_MUSIC:
                self.session.toggle_music()
            elif translated.action is SystemAction.CONFIRM:
                self.session.confirm()
            elif translated.command is not None:
                self.session.handle_command(translated.command)
        self.session.release_lagged_commands()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    pygame.init()
    try:
        GlitchRunnerApp().run()
    finally:
        pygame.quit()

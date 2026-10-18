from collections.abc import Callable

import pygame

from glitch_runner.application.ports import Clock
from glitch_runner.application.session import GameSession, GameState
from glitch_runner.config import (
    BLACK,
    DEBUG_MODE,
    GLITCH_COLOR,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    VERSION,
    WHITE,
)
from glitch_runner.domain.level import Level
from glitch_runner.presentation.background import Background
from glitch_runner.presentation.effects import ScreenEffectsRenderer, apply_level_glitch
from glitch_runner.presentation.sprites import (
    EnemySprites,
    ExitSprite,
    PlatformSprites,
    PlayerSprite,
)

OVERLAY_COLOR = (0, 0, 0, 128)
GAME_OVER_COLOR = (255, 0, 0)
LEVEL_COMPLETE_COLOR = (0, 255, 0)
GAME_COMPLETED_COLOR = (0, 255, 255)

MENU_LINES = (
    "Navigate through glitchy levles to reach the exit portal",
    "Watch out for enemys and random glitches!",
    "",
    "Controls:",
    "Arrow Keys: Move",
    "Space: Jump/Double Jump",
    "M: Toggle Music On/Off",
    "",
    "Press ENTER to Start",
)

DEBUG_CONTROLS = (
    "Controls:",
    "Arrow Keys: Move",
    "Space: Jump/Double Jump",
    "Wall Slide: Touch wall while falling",
    "F3: Toggle Debug Mode",
)


BackgroundLoader = Callable[[int], pygame.Surface | None]


class LevelView:
    def __init__(self, level: Level, background_image: pygame.Surface | None) -> None:
        self.background = Background(level.number, background_image)
        self.exit = ExitSprite(level.exit.size)

    def advance(self) -> None:
        self.background.update()
        self.exit.advance()


class GameRenderer:
    def __init__(
        self,
        screen: pygame.Surface,
        player_frames: dict[str, list[pygame.Surface]],
        levels: list[Level],
        clock: Clock,
        fps_source: pygame.time.Clock,
        background_loader: BackgroundLoader,
    ) -> None:
        self.screen = screen
        self.clock = clock
        self.fps_source = fps_source
        self.font = pygame.font.SysFont(None, 24)
        self.title_font = pygame.font.SysFont(None, 48)
        self.canvas = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.player = PlayerSprite(player_frames)
        self.enemies = EnemySprites()
        self.platforms = PlatformSprites()
        self.effects = ScreenEffectsRenderer()
        self.level_views = {
            level.number: LevelView(level, background_loader(level.number)) for level in levels
        }

    def advance(self, session: GameSession) -> None:
        self.level_views[session.current_level.number].advance()
        self.player.advance(session.player)

    def render(self, session: GameSession) -> None:
        if session.state is GameState.MENU:
            self._render_menu(session)
        else:
            self._render_playing(session)
            if session.state is GameState.GAME_OVER:
                self._render_game_over(session)
            elif session.state is GameState.LEVEL_COMPLETE:
                self._render_level_complete(session)
            elif session.state is GameState.GAME_COMPLETED:
                self._render_game_completed(session)
        pygame.display.flip()

    def _render_playing(self, session: GameSession) -> None:
        self.canvas.fill(BLACK)
        glitches = session.glitches
        if glitches.screen.visible:
            self._draw_level(session.current_level)
            self.player.draw(self.canvas, session.player, self.clock.now())
        self.effects.apply(self.canvas, glitches.screen, glitches.notification(self.clock.now()))
        self.screen.blit(self.canvas, (0, 0))
        self._render_hud(session)

    def _draw_level(self, level: Level) -> None:
        view = self.level_views[level.number]
        view.background.draw(self.canvas)
        offset = level.shake.offset
        for platform in level.platforms:
            self.platforms.draw(self.canvas, platform, offset)
        self.canvas.blit(view.exit.image, level.exit.move(offset))
        for enemy in level.enemies:
            self.enemies.draw(self.canvas, enemy, offset)
        if level.glitch.enabled:
            apply_level_glitch(self.canvas, level.glitch.effect)

    def _render_hud(self, session: GameSession) -> None:
        level_label = f"Level {session.level_index + 1}: {session.current_level.name}"
        self._text(level_label, (10, 10))
        self._text(f"Lives: {session.lives}/{session.max_lives}", (10, 40))
        self._text(f"Score: {session.score}", (10, 70))
        self._text(f"Music: {_music_status(session)}", (10, 100))
        self._text_right(f"Version: {VERSION}", 10)

        labels = session.glitches.active_labels
        if labels:
            active = f"Active Glitches: {', '.join(labels)}"
            self._text(active, (10, SCREEN_HEIGHT - 30), GLITCH_COLOR)

        if DEBUG_MODE:
            self._text(f"FPS: {int(self.fps_source.get_fps())}", (SCREEN_WIDTH - 100, 40))
            for i, line in enumerate(DEBUG_CONTROLS):
                self._text(line, (SCREEN_WIDTH - 250, 70 + i * 20))

    def _render_menu(self, session: GameSession) -> None:
        self.screen.fill(BLACK)
        title = self.title_font.render("GLITCH RUNNER", True, GLITCH_COLOR)
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 100)))
        self._text_right(f"Version: {VERSION}", SCREEN_HEIGHT - 30)
        self._text(f"Music: {_music_status(session)}", (10, SCREEN_HEIGHT - 30))
        for i, line in enumerate(MENU_LINES):
            self._text_centered(line, 200 + i * 30)

    def _render_game_over(self, session: GameSession) -> None:
        self._overlay()
        self._title_centered("GAME OVER", GAME_OVER_COLOR)
        middle = SCREEN_HEIGHT // 2
        if session.lives > 1:
            self._text_centered(f"Lives remaining: {session.lives}/{session.max_lives}", middle)
            self._text_centered("Continuing...", middle + 30)
        else:
            self._text_centered("Press ENTER to return to menu", middle + 30)

    def _render_level_complete(self, session: GameSession) -> None:
        self._overlay()
        self._title_centered("LEVEL COMPLETE!", LEVEL_COMPLETE_COLOR)
        self._text_centered(f"Score: {session.score}", SCREEN_HEIGHT // 2)
        self._text_centered("Continuing to next level...", SCREEN_HEIGHT // 2 + 30)

    def _render_game_completed(self, session: GameSession) -> None:
        self._overlay()
        self._title_centered("GAME COMPLETED!", GAME_COMPLETED_COLOR)
        self._text_centered(f"Final Score: {session.score}", SCREEN_HEIGHT // 2)
        self._text_centered("Press ENTER to return to menu", SCREEN_HEIGHT // 2 + 30)
        self._text_right(f"Version: {VERSION}", SCREEN_HEIGHT - 30)

    def _overlay(self) -> None:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(OVERLAY_COLOR)
        self.screen.blit(overlay, (0, 0))

    def _title_centered(self, text: str, color: tuple[int, int, int]) -> None:
        rendered = self.title_font.render(text, True, color)
        x = SCREEN_WIDTH // 2 - rendered.get_width() // 2
        self.screen.blit(rendered, (x, SCREEN_HEIGHT // 2 - 50))

    def _text(self, text: str, position: tuple[int, int], color=WHITE) -> None:
        self.screen.blit(self.font.render(text, True, color), position)

    def _text_centered(self, text: str, y: int) -> None:
        rendered = self.font.render(text, True, WHITE)
        self.screen.blit(rendered, (SCREEN_WIDTH // 2 - rendered.get_width() // 2, y))

    def _text_right(self, text: str, y: int) -> None:
        rendered = self.font.render(text, True, WHITE)
        self.screen.blit(rendered, (SCREEN_WIDTH - rendered.get_width() - 10, y))


def _music_status(session: GameSession) -> str:
    return "ON" if session.music_muted else "MUTED"

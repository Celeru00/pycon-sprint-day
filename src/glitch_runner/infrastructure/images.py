import logging

import pygame

from glitch_runner.config import PLAYER_HEIGHT, PLAYER_WIDTH
from glitch_runner.infrastructure.resources import IMAGES_DIR

logger = logging.getLogger(__name__)

PLAYER_DIR = IMAGES_DIR / "player"
BACKGROUNDS_DIR = IMAGES_DIR / "backgrounds"

PLAYER_SHEETS = {
    "idle": "Pink_Monster_Idle_4.png",
    "run": "Pink_Monster_Run_6.png",
    "jump": "Pink_Monster_Jump_8.png",
    "fall": "Pink_Monster_Jump_8.png",
    "wall_slide": "Pink_Monster_Climb_4.png",
}

PLACEHOLDER_FILL = (0, 255, 0)
PLACEHOLDER_LINE = (0, 200, 0)

SpriteSet = dict[str, list[pygame.Surface]]


def load_player_sprites() -> SpriteSet:
    placeholders = _placeholder_sprites()
    sprites: SpriteSet = {}
    for animation, filename in PLAYER_SHEETS.items():
        frames = _load_sheet(filename)
        if frames:
            sprites[f"{animation}_right"] = frames
            sprites[f"{animation}_left"] = [_flip(frame) for frame in frames]
        else:
            sprites[f"{animation}_right"] = placeholders[f"{animation}_right"]
            sprites[f"{animation}_left"] = placeholders[f"{animation}_left"]
    return sprites


def load_background(level_number: int) -> pygame.Surface | None:
    path = BACKGROUNDS_DIR / f"level{level_number}_bg.png"
    if not path.exists():
        return None
    try:
        return pygame.image.load(path).convert()
    except pygame.error:
        logger.exception("Could not load background image %s", path)
        return None


def _load_sheet(filename: str) -> list[pygame.Surface]:
    path = PLAYER_DIR / filename
    if not path.exists():
        logger.warning("Sprite sheet not found: %s", path)
        return []
    try:
        sheet = pygame.image.load(path).convert_alpha()
    except pygame.error:
        logger.exception("Could not load sprite sheet %s", path)
        return []

    frame_count = int(path.stem.rsplit("_", 1)[-1])
    width = sheet.get_width() // frame_count
    height = sheet.get_height()
    frames = []
    for index in range(frame_count):
        frame = pygame.Surface((width, height), pygame.SRCALPHA)
        frame.blit(sheet, (0, 0), (index * width, 0, width, height))
        frames.append(frame)
    return frames


def _flip(surface: pygame.Surface) -> pygame.Surface:
    return pygame.transform.flip(surface, True, False)


def _placeholder_sprites() -> SpriteSet:
    w, h = PLAYER_WIDTH, PLAYER_HEIGHT
    base = pygame.Surface((w, h), pygame.SRCALPHA)
    base.fill(PLACEHOLDER_FILL)
    pygame.draw.rect(base, PLACEHOLDER_LINE, (0, 0, w, h), 2)
    pygame.draw.line(base, PLACEHOLDER_LINE, (0, 0), (w, h), 2)
    pygame.draw.line(base, PLACEHOLDER_LINE, (0, h), (w, 0), 2)

    jump = base.copy()
    pygame.draw.polygon(jump, PLACEHOLDER_LINE, [(0, h), (w // 2, h // 2), (w, h)], 2)

    run = base.copy()
    pygame.draw.rect(run, PLACEHOLDER_LINE, (w // 4, h // 4, w // 2, h // 2), 2)

    by_animation = {"idle": base, "run": run, "jump": jump, "fall": jump, "wall_slide": base}
    sprites: SpriteSet = {}
    for animation, surface in by_animation.items():
        sprites[f"{animation}_right"] = [surface]
        sprites[f"{animation}_left"] = [_flip(surface)]
    return sprites

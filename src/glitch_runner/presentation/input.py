from dataclasses import dataclass
from enum import Enum, auto

import pygame

from glitch_runner.domain.input import HeldKeys, PlayerCommand

KEY_DOWN_COMMANDS = {
    pygame.K_LEFT: PlayerCommand.PRESS_LEFT,
    pygame.K_RIGHT: PlayerCommand.PRESS_RIGHT,
    pygame.K_SPACE: PlayerCommand.PRESS_JUMP,
}

KEY_UP_COMMANDS = {
    pygame.K_LEFT: PlayerCommand.RELEASE_LEFT,
    pygame.K_RIGHT: PlayerCommand.RELEASE_RIGHT,
    pygame.K_SPACE: PlayerCommand.RELEASE_JUMP,
}


class SystemAction(Enum):
    QUIT = auto()
    TOGGLE_MUSIC = auto()
    CONFIRM = auto()


@dataclass(frozen=True)
class InputEvent:
    action: SystemAction | None = None
    command: PlayerCommand | None = None


def translate(event: pygame.event.Event) -> InputEvent | None:
    if event.type == pygame.QUIT:
        return InputEvent(action=SystemAction.QUIT)
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_m:
            return InputEvent(action=SystemAction.TOGGLE_MUSIC)
        if event.key == pygame.K_RETURN:
            return InputEvent(action=SystemAction.CONFIRM)
        command = KEY_DOWN_COMMANDS.get(event.key)
        return InputEvent(command=command) if command else None
    if event.type == pygame.KEYUP:
        command = KEY_UP_COMMANDS.get(event.key)
        return InputEvent(command=command) if command else None
    return None


def held_keys() -> HeldKeys:
    pressed = pygame.key.get_pressed()
    return HeldKeys(
        left=pressed[pygame.K_LEFT],
        right=pressed[pygame.K_RIGHT],
        jump=pressed[pygame.K_SPACE],
    )

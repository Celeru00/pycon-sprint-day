from dataclasses import dataclass
from enum import Enum, auto


class PlayerCommand(Enum):
    PRESS_LEFT = auto()
    PRESS_RIGHT = auto()
    PRESS_JUMP = auto()
    RELEASE_LEFT = auto()
    RELEASE_RIGHT = auto()
    RELEASE_JUMP = auto()


@dataclass(frozen=True)
class HeldKeys:
    left: bool = False
    right: bool = False
    jump: bool = False

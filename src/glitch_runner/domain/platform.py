from pygame import Rect


class Platform:
    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        self.rect = Rect(x, y, width, height)
        self.alpha = 255
        self.disappearing = False
        self.solid = True

    def start_disappearing(self) -> None:
        self.alpha = 255
        self.disappearing = True

    def fade(self, step: int) -> None:
        if not self.disappearing:
            return
        self.alpha = max(0, self.alpha - step)
        self.solid = self.alpha > 0

    def restore(self) -> None:
        self.alpha = 255
        self.disappearing = False
        self.solid = True

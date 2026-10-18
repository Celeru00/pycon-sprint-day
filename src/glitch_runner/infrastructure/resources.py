from pathlib import Path

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
IMAGES_DIR = ASSETS_DIR / "images"
SOUNDS_DIR = ASSETS_DIR / "sounds"


def first_existing(candidates: list[Path]) -> Path | None:
    return next((path for path in candidates if path.exists()), None)

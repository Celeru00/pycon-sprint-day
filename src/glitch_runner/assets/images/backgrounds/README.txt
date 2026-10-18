Background Templates for Glitch Runner
==================================

This directory should contain background images for each level in the game.

Background Image Requirements:
----------------------------

1. Create separate background images for each level:
   - level1_bg.png
   - level2_bg.png
   - level3_bg.png

2. Image dimensions should match the screen size: 800x600 pixels (matching SCREEN_WIDTH and SCREEN_HEIGHT in constants.py)

3. Format: PNG or JPG (PNG recommended for transparency support)

Background Design Suggestions:
----------------------------

Level 1 - "First Glitches":
- Color scheme: Dark blue/purple tones (30, 30, 50)
- Simple grid or circuit-like patterns
- Subtle glitch effects in the background
- Clean, minimalist design for the tutorial level

Level 2 - "Glitch Intensifies":
- Color scheme: Deep purple/magenta tones (40, 20, 60)
- More complex patterns with digital distortion
- Scattered glitch elements and data fragments
- Medium complexity with some visual noise

Level 3 - "Glitch Nightmare":
- Color scheme: Dark red/burgundy tones (60, 10, 30)
- Heavy distortion and corruption effects
- Chaotic patterns with digital artifacts
- Complex visuals with high contrast elements

Implementation Notes:
-------------------
To use these backgrounds in the game, you'll need to modify the level.py file to load and display them.
The game currently uses solid color backgrounds defined in level_data.py.

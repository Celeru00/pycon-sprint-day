Player Sprite Templates for Glitch Runner
=====================================

This directory should contain sprite sheets for the player character.

Recommended Sprite Organization:
-------------------------------

1. Create separate sprite sheets for each animation state:
   - idle_right.png
   - idle_left.png
   - run_right.png
   - run_left.png
   - jump_right.png
   - jump_left.png
   - fall_right.png
   - fall_left.png
   - wall_slide_right.png
   - wall_slide_left.png

2. Each sprite sheet should contain 4 frames of animation in a horizontal strip.

3. Recommended sprite size: 40x60 pixels per frame (matching PLAYER_WIDTH and PLAYER_HEIGHT in constants.py)

4. Total sprite sheet dimensions: 160x60 pixels (4 frames x 40 pixels width)

Sprite Sheet Format:
-------------------
For each animation state, create a horizontal strip of frames like this:

+--------+--------+--------+--------+
| Frame1 | Frame2 | Frame3 | Frame4 |
+--------+--------+--------+--------+

Color Scheme Suggestion:
----------------------
- Main Character: Green/Blue tones
- Glitch Effects: Magenta/Cyan highlights
- Outlines: Dark or contrasting colors for visibility

The game will automatically load these sprites if they exist, or fall back to colored rectangles if they don't.

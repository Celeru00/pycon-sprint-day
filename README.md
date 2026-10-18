# Glitch Runner Sprint

Glitch Runner is a small 2D platformer written in Python with [pygame](https://www.pygame.org/). You run, jump and wall-jump to the exit portal while the game randomly glitches: gravity flips, platforms vanish, your controls lag.

This repo is set up for a **beginner-friendly Python sprint**. You don't need game development experience. If you can read a Python function and run a command in a terminal, you can contribute.

- [Quick Start](#quick-start)
- [How to Play](#how-to-play)
- [How the Sprint Works](#how-the-sprint-works)
- [Sprint Tasks](#sprint-tasks)
- [Project Tour](#project-tour)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

There are two ways to get set up. **Codespaces is the easiest**: nothing to install, it runs in your browser.

### Option A: GitHub Codespaces (recommended)

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/Celeru00/Glitch-Runner-Sprint)

1. Click the button above (or on GitHub: **Code → Codespaces → Create codespace on master**).
2. Wait a few minutes while it sets up. Python, uv and all the libraries are installed for you.
3. In the terminal at the bottom, start the game:
   ```bash
   uv run glitch-runner
   ```
4. Open the **Ports** tab next to the terminal, find **Game Desktop (6080)** and click the globe icon. A new browser tab opens.
5. Click **Connect**. You'll see a desktop with the game window. Click inside the game window before pressing keys.

Leave that tab open. Every time you run the game, it appears there.

> Codespaces has no sound. Everything else works the same.

When you push your first change, GitHub will offer to create a fork for you. Say yes.

### Option B: On your own computer

**1. Install uv**

[uv](https://docs.astral.sh/uv/) installs Python and every library this project needs. You don't need to install Python yourself.

macOS / Linux:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Windows (PowerShell):

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Close and reopen your terminal, then check it worked:

```bash
uv --version
```

**2. Get the code**

Fork this repository on GitHub, then clone your fork:

```bash
git clone https://github.com/<your-username>/Glitch-Runner-Sprint.git
cd Glitch-Runner-Sprint
```

**3. Install and play**

```bash
uv sync
uv run glitch-runner
```

A game window should open. Press **Enter** to start.

### Run the checks

Whichever option you chose:

```bash
uv run pytest           # tests
uv run ruff check .     # lint
uv run ruff format .    # auto-format your code
```

If all three pass, you're ready.

---

## How to Play

| Key         | Action                                 |
| ----------- | -------------------------------------- |
| Left/Right  | Move                                   |
| Space       | Jump (press again in the air to double jump) |
| M           | Mute or unmute music                   |
| Enter       | Start / continue                       |

Slide down a wall by pushing into it while falling, then press Space to wall jump.

- **5 levels**, from "First Glitches" to "System Collapse". Levels 4 and 5 shake constantly, and level 5 adds extra screen corruption.
- **3 enemy types**: basic (patrols), jumper (hops every 2 seconds) and shooter (fires at you when you're level with it).
- **Lives** are set per level: 2 on level 1, up to 8 on level 5. Run out and you're back at the menu.
- **Score**: 1000 points per level, plus a bonus for finishing in under 60 seconds.

### Glitches

Every 10 seconds a random glitch hits for 5 seconds:

| Glitch                | Effect                          |
| --------------------- | ------------------------------- |
| Reversed Gravity      | You fall upwards                |
| Flickering Sprites    | The level blinks in and out     |
| Input Lag             | Your key presses arrive late    |
| Color Distortion      | The screen gets a colour tint   |
| Screen Shake          | The screen shakes               |
| Platform Disappear    | 1 to 3 platforms fade away      |
| Speed Change          | You move faster or slower       |
| Pixelation            | The screen goes blocky          |

---

## How the Sprint Works

1. **Pick a task** (see [Sprint Tasks](#sprint-tasks)). Tell an organiser which one you've picked so two people don't do the same one.
2. **Create a branch** for it:
   ```bash
   git checkout -b my-task-name
   ```
3. **Make your change.** Run the game often with `uv run glitch-runner` to see it working.
4. **Check your work:**
   ```bash
   uv run ruff format .
   uv run ruff check .
   uv run pytest
   ```
5. **Commit and push**, then open a pull request against this repo. In the description, say which task you did and how you tested it.

### Ground rules

- One task per pull request. Small PRs get reviewed faster.
- All three checks must pass.
- If you change game rules, add or update a test in `tests/` if you can.
- Stuck for more than 15 minutes? Ask. That's what the sprint is for.

---

## Sprint Tasks

Tasks come in four levels. Organisers will share the full list at the start of the sprint.

| Level         | What you'll do                                                        |
| ------------- | --------------------------------------------------------------------- |
| 1. Warm-up    | Change values and text: jump height, colours, menu text, key bindings |
| 2. Core       | Add a small feature: a new level, sounds, a high score, tests         |
| 3. Bug Hunt   | Track down and fix real bugs in the game                              |
| 4. Stretch    | Bigger features: a pause screen, a new enemy, a new glitch            |

New to Python or to this codebase? Start at level 1. The [Project Tour](#project-tour) shows where each kind of change lives.

---

## Project Tour

### Where to change things

| I want to...                         | Look in                                      |
| ------------------------------------ | -------------------------------------------- |
| Tweak speed, gravity, jump height    | `src/glitch_runner/config.py`                |
| Add or edit a level                  | `src/glitch_runner/domain/levels.py`         |
| Change how the player moves          | `src/glitch_runner/domain/player.py`         |
| Change enemy behaviour               | `src/glitch_runner/domain/enemy.py`          |
| Add a new glitch                     | `src/glitch_runner/domain/glitches.py` and `presentation/effects.py` |
| Change scoring, lives, game flow     | `src/glitch_runner/application/session.py`   |
| Change what's drawn on screen        | `src/glitch_runner/presentation/renderer.py` |
| Change key bindings                  | `src/glitch_runner/presentation/input.py`    |
| Add sounds                           | `src/glitch_runner/infrastructure/audio.py` and `assets/sounds/` |

### How the code is organised

The code is split into layers so you can work on one part without understanding all of it:

```
src/glitch_runner/
├── domain/            # The game rules: how things move, collide and glitch
├── application/       # The game flow: menu, playing, game over, scoring, lives
├── infrastructure/    # Talking to the computer: loading images and playing sounds
├── presentation/      # What you see and press: drawing the screen, reading keys
├── assets/            # Images and sounds
├── config.py          # Numbers you can tweak
└── app.py             # Starts the game and connects everything
tests/                 # Tests that run without opening a window
```

One rule keeps this tidy: **`domain/` never draws or plays sound.** It only works out where things are and what happens. That's why its tests run without opening a window. If your change needs something on screen, the drawing part goes in `presentation/`.

### Each frame, in order

1. `app.py` reads key presses and passes them to the `GameSession`.
2. `GameSession.update()` moves the player and enemies, applies glitches, and checks for the exit, enemy hits and lives.
3. `GameRenderer.render()` draws everything to the screen.

This runs 60 times a second.

---

## Troubleshooting

**`uv: command not found`**
Close and reopen your terminal after installing uv.

**In Codespaces: the game doesn't show up**
The game draws to the Game Desktop, not to the editor. Open the **Ports** tab, click the globe next to **Game Desktop (6080)**, then click **Connect**. If port 6080 isn't listed, add it with **Forward a Port**.

**In Codespaces: keys don't do anything**
Click inside the game window on the Game Desktop first so it has focus.

**On your own computer: "No available video device"**
pygame needs a real screen. Run it on your own desktop, not over SSH. Use Codespaces if you can't. Tests work anywhere.

**No sound**
Check your volume and press M in case music is muted. Missing sound files are skipped silently.

**pygame fails to install**
Always use `uv run ...` and not plain `python`. uv uses the Python version in `.python-version`, which pygame supports.

**Tests fail before you've changed anything**
Run `uv sync` again, then `uv run pytest`. If it still fails, tell an organiser.

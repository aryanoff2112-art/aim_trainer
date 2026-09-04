# Aim Trainer

A desktop aim-training game built with [Pygame](https://www.pygame.org/). Six training
modes, adaptive difficulty, persistent stats, achievements, and a post-session
weak-area recommendation — all in pure Python.

## Modes

| Mode | Description |
|---|---|
| **Survival** | Endless — targets grow/shrink, limited lives, difficulty ramps over time and adapts to how well you're doing. Bonus/bomb/tiny/decoy/reverse/golden target types and movement unlock at higher levels. |
| **Gridshot** | 60 seconds, one fixed-size target, replaced instantly on hit. Raw flick speed and click precision. |
| **Flick** | 20 hits, targets alternate between far-apart corners, forcing wide flicks. |
| **Reaction** | 20 hits, target appears after a randomized delay. Pure reaction time. |
| **Precision** | 20 hits, tiny targets with bullseye zone scoring. |
| **Tracking** | 45 seconds, follow a continuously moving target with your crosshair — nothing to click, scored by time-on-target. |

## Controls

- **Mouse** — aim (relative motion, scaled by your sensitivity setting)
- **Left click** — shoot
- **P** — pause / resume
- **Esc** — quit to menu mid-session (no stats recorded for an aborted run)
- **Up / Down** — change mode (menu)
- **Left / Right** — change difficulty (menu, Survival only)
- **C** — Settings
- **D** — Performance dashboard
- **R** — restart after a session
- **Esc** — quit (from the main menu)

## Installation

```bash
git clone <https://github.com/aryanoff2112-art/aim_trainer>
cd aim_trainer
pip install -r requirements.txt
python main.py
```

`numpy` is optional — it powers the synthesized sound effects. Without it the game
runs identically, just silently.

## Settings

Open **Settings** (`C` from the menu) to configure:

- Crosshair style, size, sensitivity
- Sound on/off
- FPS cap (60 / 120 / 144 / 240 / Uncapped)
- Windowed / Fullscreen display

Settings and stats are saved locally to `user_settings.json` and `stats.json`
(gitignored — these are per-player save data, not part of the source).

## Project structure

```
aim_trainer/
├── main.py                # entry point / main menu loop
├── settings.py             # constants: window size, fonts, difficulty presets
├── settings_store.py       # load/save user_settings.json
├── stats.py                 # load/save stats.json, session recording
├── achievements.py          # achievement definitions + unlock checks
├── recommendations.py       # post-session "weakest area" suggestion
├── audio.py                  # synthesized sound effects (numpy, optional)
├── particles.py              # hit-burst particle effect
├── target.py                  # Target class: growth, movement patterns, scoring zones
├── modes/
│   ├── base.py                 # GameMode base class - shared game loop, input, HUD
│   ├── single_target.py        # shared base for one-target-at-a-time modes
│   ├── survival.py
│   ├── gridshot.py
│   ├── flick.py
│   ├── precision.py
│   ├── reaction.py
│   └── tracking.py
└── ui/
    ├── menu.py                  # mode/difficulty select screen
    ├── settings_menu.py
    ├── dashboard.py              # all-time stats + recent-session chart
    ├── end_screen.py             # post-session summary
    ├── hud.py                     # in-game HUD, pause/countdown/bomb overlays
    └── crosshair.py
```

## Notes on gameplay feel

- The game reads relative mouse motion (`pygame.mouse.get_rel()`) each frame and
  scales it by your sensitivity setting, so it behaves like an FPS-style raw-input
  crosshair rather than an absolute OS cursor. The OS cursor is grabbed
  (`pygame.event.set_grab`) during a session so a fast flick can't run out of room
  at the edge of your screen.
- All movement/growth is delta-time scaled, so gameplay speed is consistent
  regardless of your FPS cap.
- Survival's difficulty adapts within a session: a rolling window of your last 10
  hit/miss outcomes nudges spawn rate up or down if you're doing consistently well
  or poorly.

## License

MIT — see [LICENSE](LICENSE).

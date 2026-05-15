# HIT137 Assignment 3 — Individual Contribution Report
**Name:** Shishir Rai
**Files:** `main.py`, `game_engine.py`
**Project:** Neon Detective: Spot the Difference

---

## Overview

My contribution covers the core game engine and application entry point for the *Neon Detective* spot-the-difference game. This includes the full GUI layout, game state management, image display pipeline, player interaction handling, scoring system, and visual feedback — all implemented using Python's `tkinter`, `OpenCV`, and `Pillow` libraries.

---

## Files

### `main.py`

The application entry point. Initialises the `tkinter` root window, instantiates `PremiumSpotGame`, and starts the main event loop.

```python
root = tk.Tk()
game = PremiumSpotGame(root)
root.mainloop()
```

This keeps the launch logic minimal and delegates all responsibility to the game engine class.

---

### `game_engine.py` — `PremiumSpotGame` class

The central class of the application. It manages the entire game lifecycle from startup to win/loss resolution.

#### Initialisation (`__init__`)

On startup, the class:
- Configures the window to 1280×820 with a fixed, non-resizable dark background
- Instantiates `ImageProcessor` for image handling
- Sets up all game state variables (`remaining`, `mistakes`, `score`, `streak`, `game_locked`, `start_time`)
- Calls `draw_background()`, `create_widgets()`, and `animate_glow()` to build and animate the UI

#### Background Rendering (`draw_background`)

Draws a stylised neon grid background using diagonal lines and gradient oval blobs directly onto a full-window `tk.Canvas`. Uses three layered ovals in deep blue and purple tones to create depth without any external image assets.

#### Widget Construction (`create_widgets`)

Builds the full UI layout across five logical zones:

| Zone | Contents |
|------|----------|
| Header | Game title and tagline |
| Control Panel | Load Image button, Reveal Clues button, status label, timer |
| Stats Panel | Four stat cards — Remaining, Mistakes, Score, Streak |
| Image Area | Two side-by-side canvases (Original Evidence / Altered Scene) |
| Bottom Bar | Gameplay tip and legend |

#### Reusable UI Components

**`create_button(parent, text, normal, hover, command)`**
Produces styled flat buttons with hover colour transitions via `<Enter>` and `<Leave>` bindings.

**`create_stat_card(parent, icon, title, value, accent)`**
Builds a fixed-size stat tile (270×72px) with an emoji icon, label, and dynamically updatable value label stored as `card.value_label`.

**`create_image_panel(parent, title, subtitle, border_color)`**
Creates a framed canvas panel with title/subtitle labels and a coloured border. Returns both the outer frame (for glow animation) and the inner canvas (for image rendering).

#### Glow Animation (`animate_glow`)

Uses `math.sin(time.time() * 2)` to pulse the border colour of the original image panel between teal shades at 120ms intervals via `root.after()`. This runs continuously throughout the session as a passive visual effect.

#### Image Loading (`load_new_image`)

Opens a file dialog filtered to `.jpg`, `.jpeg`, `.png`, and `.bmp`. On a valid selection, delegates to `ImageProcessor.load_image()` and then:
- Resets all game state
- Unlocks gameplay (`game_locked = False`)
- Starts the timer
- Calls `show_images()` and `update_labels()`

#### Image Display Pipeline

**`resize_for_display(image)`**
Scales a cv2 image to fit within the 520×415 display canvas while preserving aspect ratio. Stores `scale_x` and `scale_y` for use in coordinate mapping.

**`convert_cv_to_tk(image)`**
Converts a BGR cv2 image to an RGB `PIL.Image`, then wraps it in `ImageTk.PhotoImage` for tkinter compatibility.

**`show_images()`**
Calls both helpers and renders the original and modified images onto their respective canvases, centred.

#### Click Handling (`handle_click`, `get_image_click_position`)

`get_image_click_position` converts canvas pixel coordinates back to original image coordinates, accounting for both the display scale and the centring offset. Returns `None, None` if the click falls outside the image bounds.

`handle_click` processes each click:
- If the game is locked, exits immediately
- Plays a click sound
- Iterates over differences and checks `diff.contains_click()`
- **Correct click:** marks difference as found, increments streak, calculates score (`15 + streak × 3`), plays correct sound, draws a red circle marker
- **Wrong click:** decrements streak, deducts 5 score points, plays wrong sound; triggers game over after 3 mistakes
- **Win condition:** triggered when `remaining == 0`; calculates time bonus and shows result dialog

#### Scoring System

| Event | Score Change |
|-------|-------------|
| Correct find | +15 + (streak × 3) |
| Wrong click | −5 (min 0) |
| Time bonus (win only) | +max(0, 60 − elapsed seconds) |

The streak multiplier rewards consecutive correct clicks without misses.

#### Visual Feedback

**`draw_circle(diff, color, tag)`**
Draws two concentric ovals on both canvases to mark a found difference or clue, with a "FOUND" or "CLUE" text label above. Red (`#FF2E63`) for player-found differences; blue (`#00B4D8`) for revealed clues.

**`flash_status(text, color)`**
Creates a flicker effect on the status label by alternating colour twice at 130ms and 260ms using `root.after()`.

**`reveal_differences()`**
Clears any existing reveal markers and redraws all difference positions in blue — without locking or penalising the player.

#### Timer (`update_timer`, `calculate_time_bonus`)

A recursive `root.after(1000, self.update_timer)` loop updates the timer label in `MM:SS` format while `timer_running` is `True`. The time bonus awarded on win is `max(0, 60 − elapsed)`, capped at 60 and floored at 0.

#### Sound Effects (`play_sound`)

Uses `winsound.Beep()` (Windows only) with a `try/except ImportError` guard for cross-platform compatibility. Five distinct tones are mapped to: `click`, `correct`, `wrong`, `gameover`, and `win`.

---

## Design Decisions

**Separation of concerns:** Game logic (state, scoring, input) lives in `game_engine.py`. Image manipulation is fully delegated to `ImageProcessor`. This makes each module independently testable.

**Coordinate mapping:** Rather than working in display space, clicks are mapped back to original image coordinates before checking against stored difference bounding boxes. This ensures accuracy regardless of image size or aspect ratio.

**Graceful failure:** `winsound` is imported inside a `try/except` so the game runs without error on non-Windows systems. All state changes are guarded by `game_locked` to prevent interaction before an image is loaded or after a game ends.

**Non-destructive reveal:** The reveal feature uses a separate canvas tag (`"reveal"`) so it can be toggled without affecting found-difference markers (`"found"`). The game continues uninterrupted after revealing clues.

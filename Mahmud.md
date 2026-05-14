# `gui.py` — Implementation Report

## Overview

`gui.py` defines the `GUIManager` class, responsible for all visual rendering and widget construction in the Neon Detective game. In the current codebase, `GUIManager` is instantiated as a helper inside `PremiumSpotGame` (`game_engine.py`), and several of its methods are duplicated directly on `PremiumSpotGame` itself. The report below covers every method in `gui.py`, what it does, and how it integrates with the broader game.

---

## Class: `GUIManager`

### Constructor — `__init__(self, root, game)`

Stores two references:

- `self.root` — the `tk.Tk` root window passed in from `main.py`
- `self.game` — the `PremiumSpotGame` instance

`GUIManager` does not build any widgets on construction. All rendering happens through the methods described below.

---

### Method: `draw_background(self)`

Renders the animated dark background on `self.game.bg_canvas`. Three visual layers are drawn:

1. **Diagonal grid lines** — two sets of angled lines (`#0E1B3D` and `#0B1633`) create a subtle crosshatch across the 1280×820 canvas.
2. **Ambient glow ovals** — three large, soft-edged ovals (`#102A56`, `#28124D`, `#0B3A4A`) placed off-centre to simulate depth lighting.
3. **Tag `"bg"`** — every element receives this tag so the canvas can call `.delete("bg")` and fully redraw without affecting other layers (image canvases, circles, etc.).

This method is also duplicated verbatim on `PremiumSpotGame.draw_background()` and called during `__init__` there. The duplication means changes to the background must be made in both places.

---

### Method: `create_button(self, parent, text, normal, hover, command)`

A factory that returns a styled `tk.Button`. Key properties:

| Property | Value |
|---|---|
| Font | Segoe UI, 11pt, bold |
| Relief | flat |
| Size | width=20, height=2 |
| Cursor | hand2 |
| Hover effect | `<Enter>` / `<Leave>` bindings swap `bg` between `normal` and `hover` colours |

The caller supplies both colour states and the command callback. This method is also duplicated on `PremiumSpotGame`, where it is called during `create_widgets()` to produce the "Load Case Image" and "Reveal All 5 Clues" buttons.

---

### Method: `create_stat_card(self, parent, icon, title, value, accent)`

Builds a fixed-size stat display card (`270×72 px`, background `#171B3A`) and returns it as a `tk.Frame`. Each card contains:

- An emoji icon label on the left, coloured with the `accent` colour
- A stacked text block on the right:
  - A small uppercase title label (`#8A91B4`)
  - A large value label in the `accent` colour, stored as `card.value_label`

The `.value_label` attribute is the live update target. `PremiumSpotGame.update_labels()` calls `.config(text=...)` on it whenever score, streak, remaining, or mistake counts change. Four cards are created in `create_widgets()` for Remaining, Mistakes, Score, and Streak.

This method is duplicated on `PremiumSpotGame` as well.

---

### Method: `create_image_panel(self, parent, title, subtitle, border_color)`

Assembles a labelled image panel and returns a `(outer_frame, canvas)` tuple.

Structure:

```
outer (tk.Frame, bg=border_color, padx/pady=3)  ← coloured border
  └── inner (tk.Frame, bg="#151B34")
        ├── title label (white, 14pt bold)
        ├── subtitle label (muted blue, 9pt)
        └── canvas (display_width × display_height, bg="#DDE2EA")
```

The canvas dimensions come from `self.game.display_width` and `self.game.display_height` (both set to 520×415 in `PremiumSpotGame.__init__`). `game_engine.py` calls this method twice:

- **Original panel** — border `#00D4AA` (teal), title "ORIGINAL EVIDENCE"
- **Modified panel** — border `#FFD166` (amber), title "ALTERED SCENE"

The returned canvas objects (`self.original_canvas`, `self.modified_canvas`) are used throughout `game_engine.py` for image rendering and circle drawing.

---

### Method: `animate_glow(self)`

Drives a continuous sine-wave colour animation on `self.game.original_panel` (the teal border frame of the original image). On each tick:

1. Reads `time.time()` and computes `glow = int(120 + 60 * sin(t * 2))` — a value cycling between 60 and 180.
2. Constructs a hex colour using `glow` for the green and blue channels.
3. Calls `.config(bg=color)` on `self.game.original_panel`.
4. Schedules itself again via `self.root.after(120, self.animate_glow)` (~8 fps).

The `try/except` block silences any errors that occur if the panel has been destroyed. This method is also duplicated on `PremiumSpotGame` and called from its `__init__`.

---

## Duplication with `game_engine.py`

The five methods in `GUIManager` — `draw_background`, `create_button`, `create_stat_card`, `create_image_panel`, and `animate_glow` — are all present as methods on `PremiumSpotGame` as well. `PremiumSpotGame` never instantiates or calls `GUIManager`; it calls its own copies directly.

This means `GUIManager` is currently unused at runtime. To make the separation meaningful, `PremiumSpotGame.__init__` would need to instantiate `GUIManager` and delegate the duplicated calls to it, removing the redundant copies from `game_engine.py`.

---

## Dependency Map

```
gui.py
  imports:  tkinter, time, math
  reads:    self.game.bg_canvas
            self.game.display_width / display_height
            self.game.original_panel
  used by:  game_engine.py (PremiumSpotGame) — currently only via duplication
```

---

## Summary

`GUIManager` provides five clean, reusable methods covering background rendering, button and card factories, image panel assembly, and border animation. The class is well-scoped and has no game-logic dependencies beyond the few canvas and dimension attributes it reads from `self.game`. The main outstanding issue is that all five methods are duplicated on `PremiumSpotGame`, so `GUIManager` is never actually called. Removing the duplicates from `game_engine.py` and wiring `PremiumSpotGame` to delegate to a `GUIManager` instance would resolve this and make the separation of concerns real.

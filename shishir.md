# Assignment 3 — HIT137
## Software Report: `main.py` and `game_engine.py`
**Author:** Shishir Rai
**Project:** Spot the Difference Game
**Repository:** [Assignment3-HIT137](https://github.com/Shishireno/Assignment3-HIT137)

---

## Overview

This report covers the two files I was responsible for in the group project: `main.py` and `game_engine.py`. Together these files form the entry point and core game logic of the Spot the Difference application — a desktop game built using Python, Tkinter, and OpenCV where the player must find 5 differences between an original and a modified version of a loaded image.

---

## File 1: `main.py`

### Purpose
`main.py` is the entry point of the application. Its sole responsibility is to initialise the Tkinter root window, create an instance of the game, and start the main event loop.

### Code

```python
import tkinter as tk
from game_engine import PremiumSpotGame

root = tk.Tk()
game = PremiumSpotGame(root)
root.mainloop()
```

### Breakdown

| Line | Description |
|------|-------------|
| `import tkinter as tk` | Imports the Tkinter GUI library |
| `from game_engine import PremiumSpotGame` | Imports the main game class |
| `root = tk.Tk()` | Creates the root application window |
| `game = PremiumSpotGame(root)` | Initialises the game and builds the UI |
| `root.mainloop()` | Starts the event loop — keeps the window open and responsive |

### Design Decision
Keeping `main.py` minimal and separate from the game logic follows good software design practice (separation of concerns). Any future changes to the game logic do not require touching the entry point.

---

## File 2: `game_engine.py`

### Purpose
`game_engine.py` contains the `PremiumSpotGame` class which manages the entire game — building the UI, loading images, displaying them side by side, handling player clicks, detecting correct finds, tracking score, and triggering win/lose conditions.

### Dependencies

| Import | Purpose |
|--------|---------|
| `tkinter` | GUI framework for windows, buttons, canvases, labels |
| `tkinter.filedialog` | Opens the file picker dialog for image selection |
| `tkinter.messagebox` | Displays win and game over popups |
| `ImageProcessor` | Loads the image and generates the 5 differences |
| `GUIManager` | Resizes and converts images for display |

---

### Class: `PremiumSpotGame`

#### `__init__(self, root)`
Initialises the game state and calls `create_widgets()` to build the UI.

| Attribute | Type | Description |
|-----------|------|-------------|
| `self.processor` | `ImageProcessor` | Handles image loading and difference generation |
| `self.gui` | `GUIManager` | Handles image resizing and format conversion |
| `self.remaining` | `int` | Number of differences still to find (starts at 5) |
| `self.mistakes` | `int` | Number of wrong clicks made by the player |
| `self.display_width` | `int` | Canvas width in pixels (500) |
| `self.display_height` | `int` | Canvas height in pixels (400) |
| `self.scale` | `float` | Scale factor used to map canvas coords to image coords |
| `self.offset_x` | `int` | Horizontal offset for centred image on canvas |
| `self.offset_y` | `int` | Vertical offset for centred image on canvas |

---

#### `create_widgets(self)`
Builds the full UI layout:
- **Top bar** — Load Image button on the left, status label on the right
- **Left canvas** — Displays the original image, labelled "Original"
- **Right canvas** — Displays the modified image, labelled "Find the Differences"
- **Click binding** — `<Button-1>` bound to `handle_click` on the right canvas only

---

#### `load_new_image(self)`
Opens a file dialog filtered to `.jpg`, `.png`, and `.bmp`. On a valid selection:
1. Passes the path to `ImageProcessor.load_image()`
2. Resets `remaining` to 5 and `mistakes` to 0
3. Updates the status label
4. Calls `show_images()` to render both canvases

---

#### `show_images(self)`
Renders both images and calculates scale and offset for click mapping:
scale = min(display_width / orig_width, display_height / orig_height)
offset_x = (display_width - scaled_width) // 2
offset_y = (display_height - scaled_height) // 2

---

#### `handle_click(self, event)`
Converts canvas click to original image coordinates:
img_x = (event.x - offset_x) / scale
img_y = (event.y - offset_y) / scale
Checks all unfound differences. Correct click → highlight and decrement remaining. Wrong click → increment mistakes. Win at 0 remaining, game over at 5 mistakes.

---

#### `highlight_difference(self, diff)`
Draws a green rectangle on both canvases over the found difference using reverse coordinate mapping.

---

#### `update_status(self)`
Updates the top label to show current `Remaining` and `Mistakes` count.

---

## How the Files Work Together
main.py
└── creates PremiumSpotGame (game_engine.py)
├── uses ImageProcessor  → loads image, generates 5 differences
├── uses GUIManager      → resizes and converts images for display
├── displays original + modified side by side on two canvases
├── listens for clicks on modified canvas
└── checks clicks against difference regions → win/lose logic

---

## Summary

| File | Role | Key Responsibility |
|------|------|--------------------|
| `main.py` | Entry point | Starts the application |
| `game_engine.py` | Game controller | UI, click detection, scoring, win/lose logic |

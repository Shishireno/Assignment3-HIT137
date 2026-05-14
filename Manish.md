# Assignment 3 — HIT137

## Software Report: `difference.py` and `image_processor.py`

**Project:** Spot the Difference Game  
**Repository:** Assignment3-HIT137

---

## Overview

This report covers the two files I was responsible for in the group project: `difference.py` and `image_processor.py`. Together these files form the image processing and difference detection layer of the Spot the Difference application — a desktop game built using Python, Tkinter, and OpenCV where the player must find 5 differences between an original and a modified version of a loaded image.

---

# File 1: `difference.py`

## Purpose

difference.py defines the Difference class, a data model that represents a single hidden alteration placed in the modified image. It stores the position, size, and type of each alteration, and provides helper methods used by the game engine for click detection and circle drawing.

## Code

```python
class Difference:
    def __init__(self, x, y, w, h, diff_type):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.diff_type = diff_type
        self.found = False

    def contains_click(self, x, y, tolerance=25):
        return (
            self.x - tolerance <= x <= self.x + self.w + tolerance and
            self.y - tolerance <= y <= self.y + self.h + tolerance
        )

    def get_center(self):
        center_x = self.x + self.w // 2
        center_y = self.y + self.h // 2
        return center_x, center_y

    def get_radius(self):
        return max(self.w, self.h) // 2
```

## Constructor Attributes

| Attribute | Type | Description |
|------------|------|-------------|
| self.x | int | Left edge of the altered region, in original image pixels |
| self.y | int | Top edge of the altered region, in original image pixels |
| self.w | int | Width of the altered bounding box |
| self.h | int | Height of the altered bounding box |
| self.diff_type | str | String identifier for the alteration type (e.g. "blur", "colour_shift") |
| self.found | bool | Toggled to True when the player clicks correctly; prevents double-counting |

---

## Methods

### contains_click(self, x, y, tolerance=25) → bool

Checks whether a player's click lands on this difference. Expands the bounding box by tolerance pixels on all sides before testing.

| Parameter | Description |
|------------|-------------|
| x, y | Click coordinates in original image pixel space |
| tolerance | Hit-test expansion in pixels (default 25) — gives fair, forgiving detection |

```python
def contains_click(self, x, y, tolerance=25):
    return (
        self.x - tolerance <= x <= self.x + self.w + tolerance and
        self.y - tolerance <= y <= self.y + self.h + tolerance
    )
```

The tolerance is applied in image-pixel space after the inverse scaling transform has been applied by the game engine, keeping detection accuracy consistent regardless of window size.

### get_center(self) → tuple(int, int)

Returns the pixel coordinates of the bounding box centre. Used by the game engine to position the feedback circle on both canvases.

```python
def get_center(self):
    center_x = self.x + self.w // 2
    center_y = self.y + self.h // 2
    return center_x, center_y
```

### get_radius(self) → int

Returns half the length of the longer edge of the bounding box. Used as the base radius when drawing highlight circles, ensuring the circle fully encloses the altered region regardless of aspect ratio.

```python
def get_radius(self):
    return max(self.w, self.h) // 2
```

## Design Decision

All coordinates are stored in full-resolution image pixel space, not display-canvas space. This decouples the data model from the view — the display size can change freely without touching this class. Only the found flag changes during gameplay; the geometry attributes are set once at construction and never modified.

---

# File 2: `image_processor.py`

## Purpose

image_processor.py contains the ImageProcessor class which handles all image loading and alteration. It reads an image from disk, creates an independent modified copy, randomly plants five non-overlapping hidden differences across it, and stores the resulting Difference objects. The game engine reads three public attributes from this class: original, modified, and differences.

## Dependencies

| Import | Purpose |
|----------|----------|
| cv2 | Image loading, pixel operations (blur, colour shift, brightness, drawing) |
| random | Random box placement, size selection, and alteration type selection |
| tkinter.messagebox | Displays error and warning dialogs to the user |
| Difference | Imported from difference.py; one instance created per successful alteration |

---

# Class: ImageProcessor

## __init__(self)

Initialises the three public attributes to None and an empty list.

| Attribute | Type | Description |
|------------|------|-------------|
| self.original | ndarray | Unmodified BGR image array loaded by OpenCV |
| self.modified | ndarray | Independent copy of the image with all alterations applied |
| self.differences | list | List of Difference objects, one per alteration placed |

## load_image(self, path) → bool

Reads the image from disk and resets all internal state before generating new differences.

```python
def load_image(self, path):
    image = cv2.imread(path)
    if image is None:
        messagebox.showerror("Error", "Image could not be loaded.")
        return False
    self.original = image
    self.modified = image.copy()
    self.differences = []
    self.create_differences()
    if len(self.differences) < 5:
        messagebox.showwarning("Warning", "Could not create all 5 clues. Please use a bigger image.")
    return True
```

| Step | Description |
|--------|-------------|
| cv2.imread(path) | Supports JPEG, PNG, BMP, TIFF, and WebP formats |
| image is None check | Shows an error dialog and returns False if the file cannot be opened |
| image.copy() | Creates a fully independent array — edits to modified never affect original |
| self.differences = [] | Clears state from any previous round |
| len < 5 warning | Triggers only for images too small to place all five non-overlapping boxes |

---

## check_overlap(self, new_box, boxes) → bool

```python
def check_overlap(self, new_box, boxes):
    x, y, w, h = new_box
    padding = 35
    for bx, by, bw, bh in boxes:
        if not (
            x + w + padding < bx or
            x > bx + bw + padding or
            y + h + padding < by or
            y > by + bh + padding
        ):
            return True
    return False
```

---

## How the Files Work Together

```text
main.py
└── creates PremiumSpotGame (game_engine.py)
    ├── creates ImageProcessor (image_processor.py)
    │   ├── load_image()
    │   ├── create_differences()
    │   ├── apply_difference()
    │   └── stores Difference objects (difference.py)
    │       ├── contains_click()
    │       ├── get_center()
    │       └── get_radius()
    ├── displays original + modified side by side on two canvases
    ├── maps click coordinates from canvas space → image pixel space
    └── calls diff.contains_click()
```

---

# Summary

| File | Role | Key Responsibility |
|-------|-------|-------------------|
| difference.py | Data model | Stores position, type, and found state of each alteration; provides hit-testing and geometry helpers |
| image_processor.py | Processing engine | Loads images, generates 5 randomised non-overlapping alterations, manages original and modified arrays |

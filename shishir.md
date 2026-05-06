# HIT137 Assignment 3 — Contribution Report
## Student: Shishir Rai | Role: Game Logic & Entry Point

---

## Overview

My contribution to the Spot the Difference game covers the core game logic, state management, and the application entry point. I was responsible for two files: `game_state.py` and `main.py`. These form the backbone of the application — without the game logic layer, neither the GUI nor the image processor would have anything to connect to.

---

## Files Contributed

| File | Responsibility |
|------|---------------|
| `game_state.py` | Game logic, click detection, mistake tracking, OOP inheritance |
| `main.py` | Entry point, wires all three components together |

---

## game_state.py

### Classes Implemented

#### 1. `GameState` (Base Class)
The `GameState` class manages all state for a single round of the game. It encapsulates variables such as mistake count, found count, and lock status, and exposes methods that the GUI calls in response to user interaction.

**Key attributes:**
- `mistakes` — tracks how many incorrect clicks the player has made
- `found_count` — tracks how many differences have been found
- `is_locked` — becomes `True` when the player reaches 3 mistakes, disabling further clicks
- `is_complete` — becomes `True` when all 5 differences are found
- `differences` — stores the list of `DifferenceRegion` objects passed in from `ImageProcessor`

**Key methods:**

`load_new_round(differences)` — Resets all state variables for a fresh image load and accepts a new list of `DifferenceRegion` objects from the image processor.

`check_click(px, py, scale_factor)` — The most important method in the class. When the player clicks on the modified image canvas, the GUI passes the click coordinates here. The method:
1. Returns `"locked"` immediately if the game is locked or complete
2. Converts display-space coordinates back to original image coordinates using the scale factor
3. Iterates through all unfound `DifferenceRegion` objects and checks if the click falls within any of them using the region's `contains_point()` method
4. If a match is found, marks the region as found, increments `found_count`, and returns `"found"`
5. If no match, increments the mistake counter, locks the game if mistakes reach 3, and returns `"mistake"`

`reveal_all()` — Marks all unfound regions as found, locks the game, and returns the list of newly revealed regions so the GUI can draw blue circles on them.

`get_status_text()` — Returns a human-readable string reflecting the current game state, displayed in the status bar at the bottom of the window.

---

#### 2. `ScoreTracker` (Inherits `GameState`)
`ScoreTracker` extends `GameState` to add cumulative score tracking across multiple image rounds. This satisfies the assignment's inheritance and polymorphism requirements.

**Additional attributes:**
- `total_found` — cumulative differences found across all rounds
- `total_mistakes` — cumulative mistakes across all rounds
- `rounds_played` — number of images loaded and played

**Overridden method:**

`load_new_round(differences)` — Overrides the parent method to first save the current round's stats into the cumulative totals before calling `super().load_new_round()` to reset the round state. This demonstrates polymorphism — the GUI only ever calls `load_new_round()`, but gets different behaviour depending on whether it's working with a `GameState` or `ScoreTracker` instance.

`get_cumulative_summary()` — Returns a formatted summary string shown in the top-right of the toolbar, e.g. `Total Score: 9 found | 6 mistakes | 4 image(s) played`.

---

### OOP Concepts Demonstrated

| Concept | Where Applied |
|---------|--------------|
| **Encapsulation** | All game variables are private to `GameState`, exposed only through methods |
| **Constructor** | `__init__` initialises all state in both classes |
| **Inheritance** | `ScoreTracker` inherits from `GameState` using `super()` |
| **Polymorphism** | `load_new_round()` is overridden in `ScoreTracker` with extended behaviour |
| **Class Interaction** | `GameState` interacts with `DifferenceRegion` objects from `ImageProcessor` |

---

## main.py

`main.py` serves as the entry point for the entire application. It is responsible for instantiating the three core components and wiring them together before starting the Tkinter event loop.

```python
def main():
    root = tk.Tk()
    image_processor = ImageProcessor()   # Manish
    game_state = ScoreTracker()          # Shishir
    ui = GameUI(root, game_state, image_processor)  # Mahmud
    root.mainloop()
```

This design follows the **separation of concerns** principle — each class handles one layer of the application (image processing, game logic, and UI), and `main.py` simply connects them. This makes the codebase easy to maintain and test independently.

---

## Integration with Group Members

| Integration Point | My Role |
|------------------|---------|
| `ImageProcessor` → `GameState` | My `load_new_round()` accepts `DifferenceRegion` objects generated by Manish's `ImageProcessor` |
| `GameState` → `GameUI` | My `check_click()`, `reveal_all()`, and status methods are called directly by Mahmud's `GameUI` event handlers |
| `main.py` | I wire all three components together and pass them as dependencies |

---

## Testing

The game was tested end-to-end before group submission. All features tied to my component were verified:

- Correct click returns `"found"` and increments `found_count` 
- Incorrect click returns `"mistake"` and increments mistake counter 
- Third mistake locks the game and triggers a warning popup 
- `reveal_all()` returns unrevealed regions and locks interaction 
- Completion is detected when all 5 differences are found 
- Cumulative score updates correctly across multiple image loads 
- Status bar reflects correct state at all times 

---

## GitHub Contribution

- **Repository:** https://github.com/Shishireno/Assignment3-HIT137
- **Files committed:** `game_state.py`, `main.py`, `requirements.txt`, `github_link.txt`
- **Commit message:** `Add game logic, entry point and requirements - Shishir`

---

*Report prepared by Shishir Rai — HIT137 Assignment 3, Semester 1 2026*

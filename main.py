"""
main.py
=======
Entry point for the HIT137 Assignment 3 — Spot the Difference Game.

This file wires together the three main components:
    - ImageProcessor  (Manish)   — OpenCV image loading and alteration
    - ScoreTracker    (Shishir)  — Game logic and state management
    - GameUI          (Mahmud)   — Tkinter GUI and user interaction

Run with:
    python main.py

Requirements:
    pip install opencv-python pillow numpy
"""

import tkinter as tk
from image_processor import ImageProcessor
from game_state import ScoreTracker
from game_ui import GameUI


def main():
    """Initialise and launch the Spot the Difference application."""
    # Create Tkinter root window
    root = tk.Tk()

    # Instantiate the three core components
    image_processor = ImageProcessor()   # Manish
    game_state = ScoreTracker()          # Shishir
    ui = GameUI(root, game_state, image_processor)  # Mahmud

    # Start the Tkinter event loop
    root.mainloop()


if __name__ == "__main__":
    main()

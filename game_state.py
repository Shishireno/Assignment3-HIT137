"""
game_state.py
=============
Shishir's (Zero's) responsibility — Game logic, state management, and click detection.

Classes:
    - GameState: Manages all game data and business logic
    - ScoreTracker: Tracks cumulative score across multiple images (inherits GameState)
"""


class GameState:
    """
    Manages the state of the current round of the game.

    Demonstrates:
        - Encapsulation of game variables
        - Constructor initialisation
        - Methods for game actions
        - Class interaction with ImageProcessor's DifferenceRegion objects

    Attributes:
        MAX_MISTAKES (int): Maximum allowed mistakes per image
        NUM_DIFFERENCES (int): Total differences per image
        mistakes (int): Current mistake count
        found_count (int): Number of differences found this round
        is_locked (bool): Whether clicks are disabled (3 mistakes reached)
        is_complete (bool): Whether all differences have been found
        differences (list): List of DifferenceRegion objects from ImageProcessor
    """

    MAX_MISTAKES = 3
    NUM_DIFFERENCES = 5

    def __init__(self):
        self.mistakes = 0
        self.found_count = 0
        self.is_locked = False
        self.is_complete = False
        self.differences = []

    def load_new_round(self, differences):
        """
        Reset state for a new image/round.

        Args:
            differences (list): List of DifferenceRegion objects from ImageProcessor
        """
        self.mistakes = 0
        self.found_count = 0
        self.is_locked = False
        self.is_complete = False
        self.differences = differences

    def check_click(self, px, py, scale_factor=1.0):
        """
        Process a click on the modified image.

        Converts display coordinates back to original image coordinates,
        then checks against all unfound difference regions.

        Args:
            px (int): X coordinate of click in display space
            py (int): Y coordinate of click in display space
            scale_factor (float): Scale used to resize the image for display

        Returns:
            str: One of "found", "mistake", "locked", "already_found"
        """
        if self.is_locked or self.is_complete:
            return "locked"

        # Convert display coordinates to original image coordinates
        orig_x = int(px / scale_factor)
        orig_y = int(py / scale_factor)

        for region in self.differences:
            if region.found:
                continue
            if region.contains_point(orig_x, orig_y):
                region.found = True
                self.found_count += 1
                if self.found_count >= self.NUM_DIFFERENCES:
                    self.is_complete = True
                return "found"

        # No match — it's a mistake
        self.mistakes += 1
        if self.mistakes >= self.MAX_MISTAKES:
            self.is_locked = True
        return "mistake"

    def reveal_all(self):
        """
        Mark all unfound differences as revealed.
        Locks further interaction.

        Returns:
            list: DifferenceRegion objects that were revealed (not yet found)
        """
        revealed = []
        for region in self.differences:
            if not region.found:
                region.found = True
                revealed.append(region)
        self.is_locked = True
        return revealed

    def get_remaining(self):
        """Return the number of differences still unfound."""
        return self.NUM_DIFFERENCES - self.found_count

    def get_status_text(self):
        """
        Return a human-readable status string for display.

        Returns:
            str: Status message
        """
        if self.is_complete:
            return "🎉 All differences found!"
        if self.is_locked:
            return f"❌ Too many mistakes! Found: {self.found_count}/{self.NUM_DIFFERENCES}"
        return f"Remaining: {self.get_remaining()}   Mistakes: {self.mistakes}/{self.MAX_MISTAKES}"


class ScoreTracker(GameState):
    """
    Extends GameState to track cumulative score across multiple images.

    Demonstrates:
        - Inheritance from GameState
        - Polymorphism: overrides load_new_round to preserve cumulative data

    Attributes:
        total_found (int): Total differences found across all rounds
        total_mistakes (int): Total mistakes across all rounds
        rounds_played (int): Number of images played
    """

    def __init__(self):
        super().__init__()
        self.total_found = 0
        self.total_mistakes = 0
        self.rounds_played = 0

    def load_new_round(self, differences):
        """
        Save cumulative stats from the previous round, then reset for the new one.

        Args:
            differences (list): List of DifferenceRegion objects
        """
        # Save stats from completed round before resetting
        self.total_found += self.found_count
        self.total_mistakes += self.mistakes
        if self.rounds_played > 0 or self.found_count > 0 or self.mistakes > 0:
            self.rounds_played += 1

        # Call parent reset
        super().load_new_round(differences)

        # Count the first round
        if self.rounds_played == 0:
            self.rounds_played = 1

    def get_cumulative_summary(self):
        """
        Return a summary string of the player's cumulative performance.

        Returns:
            str: Summary text
        """
        return (
            f"Total Score: {self.total_found} found | "
            f"{self.total_mistakes} mistakes | "
            f"{self.rounds_played} image(s) played"
        )

import cv2
import random
from tkinter import messagebox
from difference import Difference


class ImageProcessor:
    def __init__(self):
        self.original = None
        self.modified = None
        self.differences = []

    def load_image(self, path):
        image = cv2.imread(path)

        if image is None:
            messagebox.showerror("Error", "Image could not be loaded.")
            return False

        self.original = image
        self.modified = image.copy()
        self.differences = []

        self.create_differences()
        return True

    def check_overlap(self, new_box, boxes):
        x, y, w, h = new_box
        padding = 22

        for bx, by, bw, bh in boxes:
            if not (
                x + w + padding < bx or
                x > bx + bw + padding or
                y + h + padding < by or
                y > by + bh + padding
            ):
                return True

        return False

    def create_differences(self):
        height, width = self.original.shape[:2]
        boxes = []

        difference_types = [
            "colour_shift",
            "blur",
            "brightness",
            "dark_patch",
            "edge_line",
            "tiny_symbol",
            "texture_noise"
        ]

        attempts = 0

        while len(self.differences) < 5 and attempts < 800:
            attempts += 1

            box_w = random.randint(48, 86)
            box_h = random.randint(48, 86)

            x = random.randint(25, width - box_w - 25)
            y = random.randint(25, height - box_h - 25)

            new_box = (x, y, box_w, box_h)

            if self.check_overlap(new_box, boxes):
                continue

            diff_type = random.choice(difference_types)

            self.apply_difference(x, y, box_w, box_h, diff_type)

            self.differences.append(
                Difference(x, y, box_w, box_h, diff_type)
            )

            boxes.append(new_box)

    def apply_difference(self, x, y, w, h, diff_type):
        roi = self.modified[y:y+h, x:x+w]

        if diff_type == "colour_shift":
            roi[:, :, 0] = cv2.add(roi[:, :, 0], 26)

        elif diff_type == "blur":
            blurred = cv2.GaussianBlur(roi, (17, 17), 0)
            self.modified[y:y+h, x:x+w] = blurred

        elif diff_type == "brightness":
            bright = cv2.convertScaleAbs(roi, alpha=1.05, beta=34)
            self.modified[y:y+h, x:x+w] = bright
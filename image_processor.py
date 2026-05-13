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

        if len(self.differences) < 5:
            messagebox.showwarning(
                "Warning",
                "Could not create all 5 clues. Please use a bigger image."
            )

        return True

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

        while len(self.differences) < 5 and attempts < 1500:
            attempts += 1

            box_w = random.randint(55, 95)
            box_h = random.randint(55, 95)

            if width <= box_w + 80 or height <= box_h + 80:
                box_w = max(25, width // 6)
                box_h = max(25, height // 6)

            x = random.randint(20, max(21, width - box_w - 20))
            y = random.randint(20, max(21, height - box_h - 20))

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
        roi = self.modified[y:y + h, x:x + w].copy()

        if diff_type == "colour_shift":
            roi[:, :, 0] = cv2.add(roi[:, :, 0], 45)
            roi[:, :, 1] = cv2.subtract(roi[:, :, 1], 25)
            self.modified[y:y + h, x:x + w] = roi

        elif diff_type == "blur":
            blurred = cv2.GaussianBlur(roi, (21, 21), 0)
            self.modified[y:y + h, x:x + w] = blurred

        elif diff_type == "brightness":
            bright = cv2.convertScaleAbs(roi, alpha=1.15, beta=45)
            self.modified[y:y + h, x:x + w] = bright

        elif diff_type == "dark_patch":
            dark = cv2.convertScaleAbs(roi, alpha=0.55, beta=0)
            self.modified[y:y + h, x:x + w] = dark

        elif diff_type == "edge_line":
            cv2.line(
                self.modified,
                (x + 8, y + h // 2),
                (x + w - 8, y + h // 2),
                (20, 20, 20),
                4
            )

        elif diff_type == "tiny_symbol":
            cv2.circle(
                self.modified,
                (x + w // 2, y + h // 2),
                min(w, h) // 4,
                (20, 20, 20),
                3
            )

            cv2.line(
                self.modified,
                (x + w // 2 - 12, y + h // 2),
                (x + w // 2 + 12, y + h // 2),
                (20, 20, 20),
                3
            )

        elif diff_type == "texture_noise":
            noise = random.randint(25, 40)
            roi[:, :, 2] = cv2.add(roi[:, :, 2], noise)
            roi[:, :, 0] = cv2.subtract(roi[:, :, 0], noise // 2)
            self.modified[y:y + h, x:x + w] = roi
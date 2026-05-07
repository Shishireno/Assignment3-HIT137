```python
import tkinter as tk
from PIL import Image, ImageTk
import cv2


class GUIManager:

    def resize_for_display(self, image, display_width, display_height):
        height, width = image.shape[:2]

        scale = min(display_width / width,
                    display_height / height)

        new_width = int(width * scale)
        new_height = int(height * scale)

        resized = cv2.resize(image, (new_width, new_height))

        return resized

    def convert_cv_to_tk(self, image):
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(image_rgb)

        return ImageTk.PhotoImage(pil_image)

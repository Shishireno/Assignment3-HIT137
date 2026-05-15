import tkinter as tk
from tkinter import filedialog, messagebox
from image_processor import ImageProcessor
from gui import GUIManager


class PremiumSpotGame:

    def __init__(self, root):
        self.root = root
        self.root.title("Spot The Difference")

        self.processor = ImageProcessor()
        self.gui = GUIManager()

        self.remaining = 5
        self.mistakes = 0

        self.display_width = 500
        self.display_height = 400

        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0

        self.create_widgets()

    def create_widgets(self):
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=10, pady=6)

        self.load_btn = tk.Button(
            top_frame,
            text="Load Image",
            command=self.load_new_image
        )
        self.load_btn.pack(side=tk.LEFT)

        self.status_label = tk.Label(
            top_frame,
            text="Remaining: 5  |  Mistakes: 0",
            font=("Arial", 12)
        )
        self.status_label.pack(side=tk.RIGHT)

        canvas_frame = tk.Frame(self.root)
        canvas_frame.pack(padx=10, pady=5)

        left_frame = tk.Frame(canvas_frame)
        left_frame.pack(side=tk.LEFT, padx=5)

        tk.Label(
            left_frame,
            text="Original",
            font=("Arial", 11, "bold")
        ).pack()

        self.canvas_original = tk.Canvas(
            left_frame,
            width=self.display_width,
            height=self.display_height,
            bg="gray20"
        )
        self.canvas_original.pack()

        right_frame = tk.Frame(canvas_frame)
        right_frame.pack(side=tk.LEFT, padx=5)

        tk.Label(
            right_frame,
            text="Find the Differences",
            font=("Arial", 11, "bold")
        ).pack()

        self.canvas_modified = tk.Canvas(
            right_frame,
            width=self.display_width,
            height=self.display_height,
            bg="gray20"
        )
        self.canvas_modified.pack()
        self.canvas_modified.bind("<Button-1>", self.handle_click)

    def load_new_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("Images", "*.jpg *.png *.bmp")]
        )

        if not path:
            return

        loaded = self.processor.load_image(path)

        if loaded:
            self.remaining = 5
            self.mistakes = 0
            self.update_status()
            self.show_images()

    def show_images(self):
        resized_orig = self.gui.resize_for_display(
            self.processor.original,
            self.display_width,
            self.display_height
        )
        self.tk_original = self.gui.convert_cv_to_tk(resized_orig)
        self.canvas_original.delete("all")
        self.canvas_original.create_image(
            self.display_width // 2,
            self.display_height // 2,
            image=self.tk_original
        )

        resized_mod = self.gui.resize_for_display(
            self.processor.modified,
            self.display_width,
            self.display_height
        )
        self.tk_modified = self.gui.convert_cv_to_tk(resized_mod)
        self.canvas_modified.delete("all")
        self.canvas_modified.create_image(
            self.display_width // 2,
            self.display_height // 2,
            image=self.tk_modified
        )

        orig_h, orig_w = self.processor.original.shape[:2]
        self.scale = min(
            self.display_width / orig_w,
            self.display_height / orig_h
        )

        new_w = int(orig_w * self.scale)
        new_h = int(orig_h * self.scale)

        self.offset_x = (self.display_width - new_w) // 2
        self.offset_y = (self.display_height - new_h) // 2

    def handle_click(self, event):
        if not self.processor.differences:
            return

        img_x = (event.x - self.offset_x) / self.scale
        img_y = (event.y - self.offset_y) / self.scale

        for diff in self.processor.differences:
            if diff.found:
                continue

            if diff.contains_click(img_x, img_y):
                diff.found = True
                self.remaining -= 1
                self.highlight_difference(diff)
                self.update_status()

                if self.remaining == 0:
                    messagebox.showinfo(
                        "You Win!",
                        f"All differences found!\nMistakes: {self.mistakes}"
                    )
                return

        self.mistakes += 1
        self.update_status()

        if self.mistakes >= 5:
            messagebox.showwarning(
                "Game Over",
                "Too many mistakes! Load a new image to try again."
            )

    def highlight_difference(self, diff):
        x1 = int(diff.x * self.scale) + self.offset_x
        y1 = int(diff.y * self.scale) + self.offset_y
        x2 = int((diff.x + diff.w) * self.scale) + self.offset_x
        y2 = int((diff.y + diff.h) * self.scale) + self.offset_y

        self.canvas_modified.create_rectangle(
            x1, y1, x2, y2,
            outline="lime green",
            width=3
        )
        self.canvas_original.create_rectangle(
            x1, y1, x2, y2,
            outline="lime green",
            width=3
        )

    def update_status(self):
        self.status_label.config(
            text=f"Remaining: {self.remaining}  |  Mistakes: {self.mistakes}"
        )

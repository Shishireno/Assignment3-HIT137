import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
from PIL import Image, ImageTk
import time
import math

try:
    import winsound
except ImportError:
    winsound = None

from image_processor import ImageProcessor


class PremiumSpotGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Neon Detective: Spot the Difference")
        self.root.geometry("1280x820")
        self.root.resizable(False, False)
        self.root.configure(bg="#070A1A")

        self.processor = ImageProcessor()

        self.display_width = 520
        self.display_height = 415
        self.scale_x = 1
        self.scale_y = 1

        self.remaining = 5
        self.mistakes = 0
        self.score = 0
        self.streak = 0
        self.game_locked = True
        self.start_time = None
        self.timer_running = False

        self.original_display = None
        self.modified_display = None

        self.bg_canvas = tk.Canvas(
            self.root,
            width=1280,
            height=820,
            bg="#070A1A",
            highlightthickness=0
        )
        self.bg_canvas.place(x=0, y=0)

        self.draw_background()
        self.create_widgets()
        self.animate_glow()

    def play_sound(self, sound_type):
        if winsound is None:
            return

        try:
            if sound_type == "click":
                winsound.Beep(800, 80)
            elif sound_type == "correct":
                winsound.Beep(1200, 120)
            elif sound_type == "wrong":
                winsound.Beep(350, 180)
            elif sound_type == "gameover":
                winsound.Beep(250, 400)
            elif sound_type == "win":
                winsound.Beep(1400, 150)
                winsound.Beep(1600, 150)
        except Exception:
            pass

    def draw_background(self):
        self.bg_canvas.delete("bg")

        for i in range(0, 1280, 40):
            self.bg_canvas.create_line(i, 0, i - 220, 820, fill="#0E1B3D", width=1, tags="bg")

        for i in range(0, 820, 38):
            self.bg_canvas.create_line(0, i, 1280, i + 180, fill="#0B1633", width=1, tags="bg")

        self.bg_canvas.create_oval(-160, -130, 400, 350, fill="#102A56", outline="", tags="bg")
        self.bg_canvas.create_oval(930, 500, 1440, 1010, fill="#28124D", outline="", tags="bg")
        self.bg_canvas.create_oval(470, 60, 820, 380, fill="#0B3A4A", outline="", tags="bg")

    def create_widgets(self):
        self.main_panel = tk.Frame(self.root, bg="#0B1026")
        self.main_panel.place(x=35, y=25, width=1210, height=770)

        self.header = tk.Frame(self.main_panel, bg="#0B1026")
        self.header.pack(fill="x", padx=28, pady=(18, 8))

        title_block = tk.Frame(self.header, bg="#0B1026")
        title_block.pack(side="left")

        tk.Label(
            title_block,
            text="🕵️ NEON DETECTIVE",
            font=("Segoe UI", 30, "bold"),
            bg="#0B1026",
            fg="#F8F7FF"
        ).pack(anchor="w")

        tk.Label(
            title_block,
            text="Spot 5 hidden image changes before your investigation fails",
            font=("Segoe UI", 12),
            bg="#0B1026",
            fg="#8DEBFF"
        ).pack(anchor="w")

       

        self.control_panel = tk.Frame(self.main_panel, bg="#111735")
        self.control_panel.pack(fill="x", padx=28, pady=8)

        self.load_btn = self.create_button(
            self.control_panel,
            "📁 LOAD CASE IMAGE",
            "#00D4AA",
            "#00A884",
            self.load_new_image
        )
        self.load_btn.grid(row=0, column=0, padx=12, pady=14)

        self.reveal_btn = self.create_button(
            self.control_panel,
            "💡 REVEAL ALL 5 CLUES",
            "#3A86FF",
            "#2667CC",
            self.reveal_differences
        )
        self.reveal_btn.grid(row=0, column=1, padx=12, pady=14)

        self.status_label = tk.Label(
            self.control_panel,
            text="Awaiting image evidence...",
            font=("Segoe UI", 12, "bold"),
            bg="#111735",
            fg="#FFD166",
            width=42,
            anchor="w"
        )
        self.status_label.grid(row=0, column=2, padx=18)

        self.timer_label = tk.Label(
            self.control_panel,
            text="⏱ 00:00",
            font=("Segoe UI", 16, "bold"),
            bg="#111735",
            fg="#FF6B6B",
            width=10
        )
        self.timer_label.grid(row=0, column=3, padx=10)

        self.stats_panel = tk.Frame(self.main_panel, bg="#0B1026")
        self.stats_panel.pack(fill="x", padx=28, pady=(4, 12))

        self.remaining_label = self.create_stat_card(self.stats_panel, "🧩", "Remaining", "5", "#00D4AA")
        self.remaining_label.grid(row=0, column=0, padx=9)

        self.mistake_label = self.create_stat_card(self.stats_panel, "⚠️", "Mistakes", "0 / 3", "#EF476F")
        self.mistake_label.grid(row=0, column=1, padx=9)

        self.score_label = self.create_stat_card(self.stats_panel, "⭐", "Score", "0", "#FFD166")
        self.score_label.grid(row=0, column=2, padx=9)

        self.streak_label = self.create_stat_card(self.stats_panel, "🔥", "Streak", "0", "#FF9F1C")
        self.streak_label.grid(row=0, column=3, padx=9)

        self.image_area = tk.Frame(self.main_panel, bg="#0B1026")
        self.image_area.pack(padx=28, pady=4)

        self.original_panel, self.original_canvas = self.create_image_panel(
            self.image_area,
            "ORIGINAL EVIDENCE",
            "Reference image",
            "#00D4AA"
        )
        self.original_panel.grid(row=0, column=0, padx=16)

        self.modified_panel, self.modified_canvas = self.create_image_panel(
            self.image_area,
            "ALTERED SCENE",
            "Click this image only",
            "#FFD166"
        )
        self.modified_panel.grid(row=0, column=1, padx=16)

        self.modified_canvas.bind("<Button-1>", self.handle_click)

        self.bottom_bar = tk.Frame(self.main_panel, bg="#111735")
        self.bottom_bar.pack(fill="x", padx=28, pady=(14, 0))

        tk.Label(
            self.bottom_bar,
            text="🎮 Tip: Reveal All 5 Clues shows blue clue circles anytime. It does not end the game.",
            font=("Segoe UI", 11),
            bg="#111735",
            fg="#DDE6ED"
        ).pack(side="left", padx=18, pady=13)

        tk.Label(
            self.bottom_bar,
            text="Red = Found   |   Blue = Clue",
            font=("Segoe UI", 11, "bold"),
            bg="#111735",
            fg="#8DEBFF"
        ).pack(side="right", padx=18)

    def create_button(self, parent, text, normal, hover, command):
        button = tk.Button(
            parent,
            text=text,
            font=("Segoe UI", 11, "bold"),
            bg=normal,
            fg="white",
            activebackground=hover,
            activeforeground="white",
            relief="flat",
            width=20,
            height=2,
            command=command,
            cursor="hand2"
        )

        button.bind("<Enter>", lambda event: button.config(bg=hover))
        button.bind("<Leave>", lambda event: button.config(bg=normal))

        return button

    def create_stat_card(self, parent, icon, title, value, accent):
        card = tk.Frame(parent, bg="#171B3A", width=270, height=72)
        card.pack_propagate(False)

        tk.Label(card, text=icon, font=("Segoe UI Emoji", 20), bg="#171B3A", fg=accent).pack(
            side="left", padx=(16, 10)
        )

        text_box = tk.Frame(card, bg="#171B3A")
        text_box.pack(side="left", fill="both", expand=True)

        tk.Label(
            text_box,
            text=title.upper(),
            font=("Segoe UI", 8, "bold"),
            bg="#171B3A",
            fg="#8A91B4"
        ).pack(anchor="w", pady=(10, 0))

        value_label = tk.Label(
            text_box,
            text=value,
            font=("Segoe UI", 17, "bold"),
            bg="#171B3A",
            fg=accent
        )
        value_label.pack(anchor="w")

        card.value_label = value_label
        return card

    def create_image_panel(self, parent, title, subtitle, border_color):
        outer = tk.Frame(parent, bg=border_color, padx=3, pady=3)
        inner = tk.Frame(outer, bg="#151B34", padx=11, pady=10)
        inner.pack()

        tk.Label(inner, text=title, font=("Segoe UI", 14, "bold"), bg="#151B34", fg="#FFFFFF").pack()
        tk.Label(inner, text=subtitle, font=("Segoe UI", 9), bg="#151B34", fg="#9AA7C7").pack(pady=(0, 7))

        canvas = tk.Canvas(
            inner,
            width=self.display_width,
            height=self.display_height,
            bg="#DDE2EA",
            highlightthickness=0
        )
        canvas.pack()

        return outer, canvas

    def animate_glow(self):
        t = time.time()
        glow = int(120 + 60 * math.sin(t * 2))
        color = f"#{0:02x}{min(255, glow + 50):02x}{min(255, glow + 80):02x}"

        try:
            self.original_panel.config(bg=color)
        except Exception:
            pass

        self.root.after(120, self.animate_glow)

    def load_new_image(self):
        path = filedialog.askopenfilename(
            title="Choose an image",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp"),
                ("JPG files", "*.jpg *.jpeg"),
                ("PNG files", "*.png"),
                ("BMP files", "*.bmp")
            ]
        )

        if not path:
            return

        loaded = self.processor.load_image(path)

        if loaded:
            self.remaining = len(self.processor.differences)
            self.mistakes = 0
            self.score = 0
            self.streak = 0
            self.game_locked = False
            self.start_time = time.time()
            self.timer_running = True

            self.show_images()
            self.update_labels()
            self.update_timer()

            self.status_label.config(
                text=f"Case opened. Find all {len(self.processor.differences)} hidden changes.",
                fg="#00D4AA"
            )

    def resize_for_display(self, image):
        height, width = image.shape[:2]
        scale = min(self.display_width / width, self.display_height / height)

        new_width = int(width * scale)
        new_height = int(height * scale)

        resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)

        self.scale_x = width / new_width
        self.scale_y = height / new_height

        return resized, new_width, new_height

    def convert_cv_to_tk(self, image):
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(image_rgb)
        return ImageTk.PhotoImage(pil_image)

    def show_images(self):
        original_resized, _, _ = self.resize_for_display(self.processor.original)
        modified_resized, _, _ = self.resize_for_display(self.processor.modified)

        self.original_display = self.convert_cv_to_tk(original_resized)
        self.modified_display = self.convert_cv_to_tk(modified_resized)

        self.original_canvas.delete("all")
        self.modified_canvas.delete("all")

        self.original_canvas.create_image(
            self.display_width // 2,
            self.display_height // 2,
            image=self.original_display
        )

        self.modified_canvas.create_image(
            self.display_width // 2,
            self.display_height // 2,
            image=self.modified_display
        )

    def get_image_click_position(self, event):
        image = self.processor.modified
        height, width = image.shape[:2]
        scale = min(self.display_width / width, self.display_height / height)

        new_width = int(width * scale)
        new_height = int(height * scale)

        x_offset = (self.display_width - new_width) // 2
        y_offset = (self.display_height - new_height) // 2

        image_x = event.x - x_offset
        image_y = event.y - y_offset

        if image_x < 0 or image_y < 0 or image_x > new_width or image_y > new_height:
            return None, None

        real_x = int(image_x * self.scale_x)
        real_y = int(image_y * self.scale_y)

        return real_x, real_y

    def handle_click(self, event):
        if self.game_locked:
            return

        self.play_sound("click")

        click_x, click_y = self.get_image_click_position(event)

        if click_x is None:
            return

        found_any = False

        for diff in self.processor.differences:
            if not diff.found and diff.contains_click(click_x, click_y):
                diff.found = True
                self.remaining -= 1
                self.streak += 1
                self.score += 15 + (self.streak * 3)
                found_any = True

                self.play_sound("correct")
                self.draw_circle(diff, "#FF2E63", tag="found")
                self.flash_status("Excellent detective work! Difference found.", "#00D4AA")
                break

        if not found_any:
            self.mistakes += 1
            self.streak = 0
            self.score = max(0, self.score - 5)

            self.play_sound("wrong")
            self.flash_status("Wrong clue. Look closer before clicking.", "#EF476F")

            if self.mistakes >= 3:
                self.game_locked = True
                self.timer_running = False

                self.play_sound("gameover")

                self.status_label.config(
                    text="Investigation failed. You can still reveal all 5 clues.",
                    fg="#EF476F"
                )

                messagebox.showwarning(
                    "Game Over",
                    "You made 3 mistakes.\nYou can still press Reveal All 5 Clues."
                )

        self.update_labels()

        if self.remaining == 0:
            self.game_locked = True
            self.timer_running = False

            bonus = self.calculate_time_bonus()
            self.score += bonus

            self.update_labels()
            self.play_sound("win")

            self.status_label.config(
                text="Case solved! All hidden changes found.",
                fg="#00D4AA"
            )

            messagebox.showinfo(
                "Case Solved",
                f"You found all clues!\nTime Bonus: {bonus}\nFinal Score: {self.score}"
            )

    def flash_status(self, text, color):
        self.status_label.config(text=text, fg=color)
        self.root.after(130, lambda: self.status_label.config(fg="#FFFFFF"))
        self.root.after(260, lambda: self.status_label.config(fg=color))

    def draw_circle(self, diff, color, tag="mark"):
        image = self.processor.modified
        height, width = image.shape[:2]
        scale = min(self.display_width / width, self.display_height / height)

        new_width = int(width * scale)
        new_height = int(height * scale)

        x_offset = (self.display_width - new_width) // 2
        y_offset = (self.display_height - new_height) // 2

        center_x = int((diff.x + diff.w / 2) / self.scale_x) + x_offset
        center_y = int((diff.y + diff.h / 2) / self.scale_y) + y_offset
        radius = int(max(diff.w, diff.h) / 2 / self.scale_x) + 10

        for canvas in [self.original_canvas, self.modified_canvas]:
            canvas.create_oval(
                center_x - radius,
                center_y - radius,
                center_x + radius,
                center_y + radius,
                outline=color,
                width=5,
                tags=tag
            )

            canvas.create_oval(
                center_x - radius - 5,
                center_y - radius - 5,
                center_x + radius + 5,
                center_y + radius + 5,
                outline=color,
                width=1,
                tags=tag
            )

            canvas.create_text(
                center_x,
                center_y - radius - 16,
                text="FOUND" if color != "#00B4D8" else "CLUE",
                fill=color,
                font=("Segoe UI", 10, "bold"),
                tags=tag
            )

    def reveal_differences(self):
        if self.processor.original is None:
            messagebox.showinfo("No Image", "Please load an image first.")
            return

        self.original_canvas.delete("reveal")
        self.modified_canvas.delete("reveal")

        for diff in self.processor.differences:
            self.draw_circle(diff, "#00B4D8", tag="reveal")

        self.status_label.config(
            text=f"All {len(self.processor.differences)} clues are revealed in blue.",
            fg="#00B4D8"
        )

    def update_timer(self):
        if not self.timer_running or self.start_time is None:
            return

        elapsed = int(time.time() - self.start_time)
        minutes = elapsed // 60
        seconds = elapsed % 60

        self.timer_label.config(text=f"⏱ {minutes:02d}:{seconds:02d}")
        self.root.after(1000, self.update_timer)

    def calculate_time_bonus(self):
        if self.start_time is None:
            return 0

        elapsed = int(time.time() - self.start_time)
        return max(0, 60 - elapsed)

    def update_labels(self):
        self.remaining_label.value_label.config(text=str(self.remaining))
        self.mistake_label.value_label.config(text=f"{self.mistakes} / 3")
        self.score_label.value_label.config(text=str(self.score))
        self.streak_label.value_label.config(text=str(self.streak))
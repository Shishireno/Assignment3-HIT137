import tkinter as tk
import time
import math


class GUIManager:
    def __init__(self, root, game):
        self.root = root
        self.game = game

    def draw_background(self):
        self.game.bg_canvas.delete("bg")

        for i in range(0, 1280, 40):
            self.game.bg_canvas.create_line(
                i, 0, i - 220, 820,
                fill="#0E1B3D",
                width=1,
                tags="bg"
            )

        for i in range(0, 820, 38):
            self.game.bg_canvas.create_line(
                0, i, 1280, i + 180,
                fill="#0B1633",
                width=1,
                tags="bg"
            )

        self.game.bg_canvas.create_oval(
            -160, -130, 400, 350,
            fill="#102A56",
            outline="",
            tags="bg"
        )

        self.game.bg_canvas.create_oval(
            930, 500, 1440, 1010,
            fill="#28124D",
            outline="",
            tags="bg"
        )

        self.game.bg_canvas.create_oval(
            470, 60, 820, 380,
            fill="#0B3A4A",
            outline="",
            tags="bg"
        )

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

        tk.Label(
            card,
            text=icon,
            font=("Segoe UI Emoji", 20),
            bg="#171B3A",
            fg=accent
        ).pack(side="left", padx=(16, 10))

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

        inner = tk.Frame(
            outer,
            bg="#151B34",
            padx=11,
            pady=10
        )

        inner.pack()

        tk.Label(
            inner,
            text=title,
            font=("Segoe UI", 14, "bold"),
            bg="#151B34",
            fg="#FFFFFF"
        ).pack()

        tk.Label(
            inner,
            text=subtitle,
            font=("Segoe UI", 9),
            bg="#151B34",
            fg="#9AA7C7"
        ).pack(pady=(0, 7))

        canvas = tk.Canvas(
            inner,
            width=self.game.display_width,
            height=self.game.display_height,
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
            self.game.original_panel.config(bg=color)
        except Exception:
            pass

        self.root.after(120, self.animate_glow)

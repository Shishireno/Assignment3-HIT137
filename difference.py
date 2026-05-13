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
    
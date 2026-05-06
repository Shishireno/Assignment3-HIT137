class Difference:
    def __init__(self, x, y, w, h, diff_type):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.diff_type = diff_type
        self.found = False

    def contains_click(self, x, y, tolerance=20):
        return (
            self.x - tolerance <= x <= self.x + self.w + tolerance and
            self.y - tolerance <= y <= self.y + self.h + tolerance
        )
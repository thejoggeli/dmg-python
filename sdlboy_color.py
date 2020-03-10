class Color:
    r = 0
    g = 0
    b = 0
    a = 0
    def __init__(self, r, g, b, a):
        self.r = r
        self.g = g
        self.b = b
        self.a = a
    def set_components(self, r, g, b, a):
        self.r = r
        self.g = g
        self.b = b
        self.a = a
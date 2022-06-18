class Offset:
    def __init__(self, top: float, right: float, bottom: float, left: float):
        self.top = top
        self.right = right
        self.bottom = bottom
        self.left = left

    def __iter__(self):
        return iter((self.top, self.right, self.bottom, self.left))

    def copy(self):
        return Offset(self.top, self.right, self.bottom, self.left)

    def __str__(self):
        return f"Offset(top={self.top}, right={self.right}, bottom={self.bottom}, left={self.left})"

    def __setitem__(self, key, value):
        self.__dict__[key] = value

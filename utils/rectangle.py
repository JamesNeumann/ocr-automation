class Rectangle:
    """
    Class for representing a rectangle
    """

    def __init__(self, x: float, y: float, width: float, height: float):
        """
        :param x: x Position of the rectangle
        :param y: y position of the rectangle
        :param width: Width of the rectangle
        :param height: Height of the rectangle
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def __str__(self):
        return f"{self.__class__.__name__}(x: {self.x}, y: {self.y}, width: {self.width}, height: {self.height})"

    def area(self) -> float:
        return self.width * self.height

    @property
    def center_x(self):
        return self.x + self.width / 2

    def move_to_center(self, rectangle):
        w2 = rectangle.width
        h2 = rectangle.height
        x2 = max(self.x + ((self.width - w2) / 2), 0)
        y2 = max(self.y + ((self.height - h2) / 2), 0)

        # if y2 < self.y or y2 + h2 > self.y + self.height:
        #     if abs(self.y - y2) > abs(h2 - self.height):
        #         y2 = y2 + abs(y2 - self.y)
        #     else:
        #         y2 = y2 + abs(y2 - self.y)

        return Rectangle(x2, y2, w2, h2)

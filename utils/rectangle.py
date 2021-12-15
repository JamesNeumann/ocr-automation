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

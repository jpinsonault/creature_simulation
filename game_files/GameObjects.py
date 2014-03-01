"""
    Holds objects that subclass the GraphNode class
    Creatures, Food, etc
"""
from pygame import draw
from GraphNode import GraphNode


class Background(GraphNode):
    """Probably be used for displaying a background image tile at some point"""
    def __init__(self, x=0, y=0, heading=0.0):
        super(Background, self).__init__(x, y, heading)

    def draw(self, screen):
        pass


class Polygon(GraphNode):
    """docstring for Polygon"""
    def __init__(self, shape, x=0, y=0, heading=0.0, color=None):
        super(Polygon, self).__init__(x, y, heading)
        self.shape = shape
        self.center = self.find_center()

    def draw_self(self, screen, window):
        # draw.polygon(screen, )
        pass

    def find_center(self):
        """Find the geometric center of the polygon"""
        pass
        

class Creature(Polygon):
    """
        Object representing the creature on screen

    """
    BASE_SHAPE = [[0,0], [5, -5], [10, 0], [10, 10], [5, 15], [0, 10], [0,0]]

    def __init__(self, x=0, y=0, heading=0.0):
        super(Creature, self).__init__(self.BASE_SHAPE, x, y, heading, color=None)


class Food(Polygon):
    """
        Object representing the creature on screen

    """
    BASE_SHAPE = [[0,0], [10, 0], [10, -10], [0, -10]]

    def __init__(self, x=0, y=0, heading=0.0):
        super(Creature, self).__init__(self.BASE_SHAPE, x, y, heading)

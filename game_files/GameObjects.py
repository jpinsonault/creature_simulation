"""
    Holds objects that subclass the GraphNode class
    Creatures, Food, etc
"""
from pygame import draw
from GraphNode import GraphNode
from operator import add


class Background(GraphNode):
    """Probably be used for displaying a background image tile at some point"""
    def __init__(self, x=0, y=0, heading=0.0):
        super(Background, self).__init__(x, y, heading)

    def draw_self(self, screen, window):
        pass


class Polygon(GraphNode):
    """docstring for Polygon"""
    def __init__(self, shape, x=0, y=0, heading=0.0, color=(255, 255, 255)):
        self.shape = shape
        super(Polygon, self).__init__(x, y, heading)
        self.color = color
        # For caching shape coords
        self.relative_shape_coords = self.shape[:]
        self.shape_screen_coords = self.shape[:]
        self.relative_center = [0, 0]

    def draw_self(self, screen, window):
        # Offset from parents
        relative_position = self.relative_position()

        self.relative_center[0] = self.center[0] + relative_position[0]
        self.relative_center[1] = self.center[1] + relative_position[1]
        if window.on_screen(self.relative_center):
            # self.calc_relative_shape_coords(relative_position)
            self.relative_shape_coords = [map(add, point, relative_position[:-1]) for point in self.shape]

            self.shape_screen_coords = [window.scale(point) for point in self.relative_shape_coords]
            # self.calc_shape_screen_coords(window)
        
            draw.polygon(screen, self.color, self.shape_screen_coords)

    def find_center(self):
        """Find the geometric center of the polygon"""
        x_mean = sum(point[0] for point in self.shape) / len(self.shape)
        y_mean = sum(point[1] for point in self.shape) / len(self.shape)

        return [x_mean, y_mean]

    def calc_shape_screen_coords(self, window):
        index = 0
        num_points = len(self.shape)
        while index < num_points:
            self.shape_screen_coords[index] = window.scale(self.relative_shape_coords[index])
            index += 1
        

class Creature(Polygon):
    """
        Object representing the creature on screen

    """
    BASE_SHAPE = [[0,0], [5, -5], [10, 0], [10, 10], [5, 15], [0, 10], [0,0]]

    def __init__(self, x=0, y=0, heading=0.0, color=None):
        super(Creature, self).__init__(self.BASE_SHAPE, x, y, heading, color)

    def move_and_rotate(self, dt):
        # self.move(x_change=dt*.1)
        self.rotate(dt*.1)


class Food(Polygon):
    """
        Object representing the creature on screen

    """
    BASE_SHAPE = [[0,0], [10, 0], [10, -10], [0, -10]]

    def __init__(self, x=0, y=0, heading=0.0):
        super(Creature, self).__init__(self.BASE_SHAPE, x, y, heading)

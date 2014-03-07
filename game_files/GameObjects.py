"""
    Holds objects that subclass the GraphNode class
    Creatures, Food, etc
"""
from pygame import draw
from GraphNode import GraphNode
from operator import add
from math import cos
from math import sin
from pprint import pprint
from PygameUtils import rotate_around
from PygameUtils import rotate_shape


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
        self.absolute_shape = [[0.0, 0.0] for x in xrange(len(self.shape))]
        self.onscreen_shape_coords = [[0.0, 0.0] for x in xrange(len(self.shape))]
        self.absolute_position = [0, 0]

    def draw_self(self, screen, window):
        if window.on_screen(self.absolute_position):
            self.onscreen_shape_coords = [window.scale(point) for point in self.absolute_shape]
        
            draw.polygon(screen, self.color, self.onscreen_shape_coords)

    def find_center(self):
        """Find the geometric center of the polygon"""
        x_mean = sum(point[0] for point in self.shape) / len(self.shape)
        y_mean = sum(point[1] for point in self.shape) / len(self.shape)

        return [x_mean, y_mean]

    def calc_absolute_position(self):
        # Get the position
        super(Polygon, self).calc_absolute_position()
        length = len(self.shape)
    
        # Offset the shape coords by our absolute_position
        offset_unrotated_shape = [[point[0] + self.unrotated_position[0], point[1] + self.unrotated_position[1]] for point in self.shape]

        # Rotate the shape around parent's center
        parent = self.parent
        if parent:
            self.absolute_shape = rotate_shape(parent.cos_radians, parent.sin_radians, offset_unrotated_shape, parent.absolute_position, parent.heading)

        self.absolute_shape = rotate_shape(self.cos_radians, self.sin_radians, self.absolute_shape, self.absolute_position, self.heading)
        

class Creature(Polygon):
    """
        Object representing the creature on screen

    """
    BASE_SHAPE = [[-5, -5], [0, -10], [5, -5], [5, 5], [0, 10], [-5, 5]]

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

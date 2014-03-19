"""
    Holds objects that subclass the GraphNode class
    Creatures, Food, etc
"""
import sys
sys.path.insert(0, '../')
from pygame import draw
from GraphNode import GraphNode
from operator import add
from math import cos
from math import sin
from math import sqrt
from pprint import pprint
from PygameUtils import rotate_around
from PygameUtils import rotate_shape

from NeuralNetworks.NeuralNetwork import NeuralNetwork
from Colors import *


class Background(GraphNode):
    """Probably be used for displaying a background image tile at some point"""
    def __init__(self, x=0, y=0, heading=0.0):
        super(Background, self).__init__(x, y, heading)

    def draw(self, screen, camera):
        pass


class Polygon(GraphNode):
    """docstring for Polygon"""
    def __init__(self, shape, x=0, y=0, heading=0.0, color=WHITE, draw_width=0):
        self.shape = shape
        super(Polygon, self).__init__(x, y, heading)
        self.color = color
        self.draw_width = draw_width
        # For caching shape coords
        self.absolute_shape = [[0.0, 0.0] for x in xrange(len(self.shape))]
        self.onscreen_shape_coords = [[0.0, 0.0] for x in xrange(len(self.shape))]
        self.absolute_position = [0, 0]

        self.bounds = self.get_bounding_square()


    def draw(self, screen, camera):
        
        self.calc_shape_rotation()
        self.onscreen_shape_coords = [camera.scale(point) for point in self.absolute_shape]
    
        if self.selected:
            draw_color = GREEN
        else:
            draw_color = self.color

        draw.polygon(screen, draw_color, self.onscreen_shape_coords, self.draw_width)

    def find_center(self):
        """Find the geometric center of the polygon"""
        x_mean = sum(point[0] for point in self.shape) / len(self.shape)
        y_mean = sum(point[1] for point in self.shape) / len(self.shape)

        return [x_mean, y_mean]

    def get_bounding_circle(self):
        greates_distance = 0
        for point in self.shape:
            distance = (point[0] * point[0]) + (point[1] * point[1])
            greates_distance = max(distance, greates_distance)

        # Return the radius of the bounding circle
        return sqrt(greates_distance)

    def get_bounding_square(self):
        min_length = 0

        for point in self.shape:
            min_length = min(point[0], point[1], min_length)

        # Returns the top left corner and the length of the square's sides
        return (min_length, min_length, abs(min_length) * 2, abs(min_length) * 2)

    def calc_shape_rotation(self):
        # Offset the shape coords by our absolute_position
        offset_unrotated_shape = [[point[0] + self.unrotated_position[0], point[1] + self.unrotated_position[1]] for point in self.shape]

        # Rotate the shape around parent's center
        parent = self.parent
        if parent:
            self.absolute_shape = rotate_shape(parent.cos_radians, parent.sin_radians, offset_unrotated_shape, parent.absolute_position, parent.heading)

        self.absolute_shape = rotate_shape(self.cos_radians, self.sin_radians, self.absolute_shape, self.absolute_position, self.heading)

    def get_bounds(self):
        bounds = self.bounds
        return (bounds[0] + self.absolute_position[0], bounds[1] + self.absolute_position[1], bounds[2], bounds[3])

    def collide_point_poly(self, point):
        """
            Returns true if point collides with this polygon
            Uses an algorithm lifted from 
                http://geospatialpython.com/2011/01/point-in-polygon.html
        """
        x, y = point
        poly = self.absolute_shape

        n = len(poly)
        inside = False

        p1x, p1y = poly[0]
        for i in range(n + 1):
            p2x, p2y = poly[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xints = (y - p1y)*(p2x - p1x)/(p2y - p1y) + p1x
                        if p1x == p2x or x <= xints:
                            inside = not inside
            p1x, p1y = p2x, p2y

        return inside

class Creature(Polygon):
    """
        Object representing the creature on screen
    """
    BASE_SHAPE = [[-5, 5], [-10, 0], [-5, -5], [5, -5], [10, 0], [5, 5]]

    def __init__(self, x=0, y=0, heading=0.0, color=WHITE):
        super(Creature, self).__init__(self.BASE_SHAPE, x, y, heading, color)

        self.nn = NeuralNetwork(3, 7, 2)
        self.nn.initialize_random_network(.2)

        # Add a vision code to the creature
        self.vision_cone = VisionCone(x=100, color=RED)
        self.vision_cone.visible = False
        self.vision_cone.reparent_to(self)
        self.vision_cone.calc_absolute_position()


    def get_stats(self):
        """
            Returns a list of strings with relevent info about this creature
            Used to display info on screen
        """
        stats = ["Creature Stats"]
        stats.append("Position: {:.0f}, {:.0f}".format(*self.absolute_position))
        stats.append("Health: {}".format(self.color))
        stats.append("More stuff")

        return stats

    def draw(self, screen, camera):
        super(Creature, self).draw(screen, camera)
        if self.selected:
            self.vision_cone.draw(screen, camera)


class Food(Polygon):
    """
        Object representing the food on screen
    """
    BASE_SHAPE = [[-20, -20], [20, -20], [20, 20], [-20, 20]]

    def __init__(self, x=0, y=0, heading=0.0, color=WHITE):
        super(Food, self).__init__(self.BASE_SHAPE, x, y, heading, color)


class VisionCone(Polygon):
    """
        A triangle for the creatures' vision
    """
    BASE_SHAPE = [[-10, 0], [30, -15], [30, 15]]

    def __init__(self, x=0, y=0, heading=0.0, color=WHITE):
        factor = 10
        scaled_shape = [[xpos*factor, ypos*factor] for xpos, ypos in self.BASE_SHAPE]
        super(VisionCone, self).__init__(scaled_shape, x, y, heading, color, 1)


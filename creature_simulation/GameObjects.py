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
from itertools import chain
from pprint import pprint
from PygameUtils import rotate_around
from PygameUtils import rotate_shape
from PygameUtils import dot_2d


from NeuralNetworks.NeuralNetwork import NeuralNetwork
from Colors import *

# utility functions
_clamp = lambda a, v, b: max(a, min(b, v))              # clamp v between a and b
_perp = lambda (x, y): [-y, x]                          # perpendicular
_prod = lambda X: reduce(mul, X)                        # product
_mag = lambda (x, y): sqrt(x * x + y * y)               # magnitude, or length
_normalize = lambda V: [i / _mag(V) for i in V]         # normalize a vector
# def _normalize(point):
#     magnitude = _mag(point)
#     if magnitude == 0.0:
#         return point
#     else:
#         return [i / magnitude for i in point] P

_intersect = lambda A, B: (A[1] > B[0] and B[1] > A[0]) # intersection test
_unzip = lambda zipped: zip(*zipped)                    # unzip a list of tuples


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

        self.num_points = len(self.shape)
        # For caching shape coords
        self.absolute_shape = [[0.0, 0.0] for x in xrange(self.num_points)]
        self.onscreen_shape_coords = [[0.0, 0.0] for x in xrange(self.num_points)]
        self.absolute_position = [0, 0]

        # Whether or not the calculation needs to be done
        self.shape_calculated = False

        self.bounds = self.get_bounding_square()


    def draw(self, screen, camera):
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
        greatest_distance = 0
        for point in self.shape:
            distance = (point[0] * point[0]) + (point[1] * point[1])
            greatest_distance = max(distance, greatest_distance)

        # Return the radius of the bounding circle
        return sqrt(greatest_distance)

    def get_bounding_square(self):
        max_radius = self.get_bounding_circle()
        return (-max_radius, -max_radius, max_radius * 2, max_radius * 2)

    def update_position(self):
        super(Polygon, self).update_position()
        self.calc_shape_rotation()

    def calc_shape_rotation(self):
        if not self.shape_calculated:
            # Offset the shape coords by our absolute_position
            offset_unrotated_shape = [[point[0] + self.unrotated_position[0], point[1] + self.unrotated_position[1]]
                                        for point in self.shape]

            # Rotate the shape around parent's center
            parent = self.parent
            if parent:
                self.absolute_shape = rotate_shape(parent.cos_radians, parent.sin_radians, offset_unrotated_shape, parent.absolute_position, parent.heading)
            self.absolute_shape = rotate_shape(self.cos_radians, self.sin_radians, self.absolute_shape, self.absolute_position, self.heading)

            self.shape_calculated = True

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

    def collide_bounds(self, other):
        a_x, a_y, a_w, a_h = self.get_bounds()
        b_x, b_y, b_w, b_h = other.get_bounds()

        a_w = a_w / 2
        a_h = a_h / 2

        a_x = a_x + a_w
        a_y = a_y + a_h

        return ((abs(a_x - b_x) < (a_w + b_w)) and
               (abs(a_y - b_y) < (a_h + b_h)))

    def _make_edges(self):
        points = self.absolute_shape

        for i, point in enumerate(points):
            next_point = points[(i + 1) % self.num_points] # x, y of next point in series
            # yield [point, next_point]
            yield [point[0] - next_point[0], point[1] - next_point[1]]

    def project(self, axis):
        """project self onto axis"""
        points = self.absolute_shape
        projected_points = [dot_2d(point, axis) for point in points]
        # return the span of the projection
        return min(projected_points), max(projected_points)

    def collide_poly(self, other):
        """
        test if other polygon collides with self using seperating axis theorem
        if collision, return projections

        arguments:
            other -- a polygon object

        returns:
            an array of projections
        """
        # a projection is a vector representing the span of a polygon projected
        # onto an axis
        projections = []

        for edge in chain(self._make_edges(), other._make_edges()):
            edge = _normalize(edge)
            # the separating axis is the line perpendicular to the edge
            axis = _perp(edge)
            self_projection = self.project(axis)
            other_projection = other.project(axis)
            # if self and other do not intersect on any axis, they do not
            # intersect in space
            if not _intersect(self_projection, other_projection):
                return False
            # find the overlapping portion of the projections
            projection = self_projection[1] - other_projection[0]
            projections.append((axis[0] * projection, axis[1] * projection))
        return projections

    def check_collision(self, other):
        """
            Does a rough check with the bounding boxes, and then
            does a poly-on-poly check
        """
        # if isinstance(self, VisionCone) and self.parent.selected and other == self.parent:
        #     if not self.collide_bounds(other) or self.collide_poly(other):
        #         import pdb; pdb.set_trace()
        #         self.collide_bounds(other)

        if self.collide_bounds(other):
            if self.collide_poly(other):
                self.on_collide(other)
                return True

        # if self.collide_poly(other):
        #     self.on_collide(other)
        #     return True

        return False
        
    def end_frame(self):
        self.shape_calculated = False
        super(Polygon, self).end_frame()


class Creature(Polygon):
    """
        Object representing the creature on screen
    """
    BASE_SHAPE = [[-5, 5], [-10, 0], [-5, -5], [5, -5], [10, 0], [5, 5]]

    MAX_HEALTH = 100

    def __init__(self, x=0, y=0, heading=0.0, color=WHITE, nn_weights=None):
        super(Creature, self).__init__(self.BASE_SHAPE, x, y, heading, color)

        self.health = self.MAX_HEALTH
        self.nn = NeuralNetwork(2, 5, 2)
        if not nn_weights:
            self.nn.initialize_random_network()
        else:
            self.nn.set_network(nn_weights)

        # Add a vision code to the creature
        # Offset in the x direction, otherwise it would be centered over the creature
        self.vision_cone = VisionCone(x=260, color=RED)
        self.vision_cone.visible = False
        self.vision_cone.reparent_to(self)

        self.speed = 0
        self.rotation = 0

        self.food_seen = 0

    def do_everyframe_action(self, time_dt, game_speed):
        self.health -= time_dt/900.0
        self.rotation = self.nn.get_outputs()[0] / 100
        self.speed = self.nn.get_outputs()[1] / 10
        self.health -= (abs(self.speed*time_dt) / 5000.0) * game_speed

        self.nn.set_inputs([self.food_seen, self.health / 100])

        if self.health <= 0:
            self.health = 0

    def get_stats(self):
        """
            Returns a list of strings with relevent info about this creature
            Used to display info on screen
        """
        stats = ["Creature Stats"]
        stats.append("Speed: {}".format(self.speed))
        stats.append("Food seen: {}".format(self.food_seen))
        stats.append("Health: {}".format(self.health))
        stats.append("Inputs: {}".format(self.nn.get_inputs()))
        stats.append("Outputs: {}".format(self.nn.get_outputs()))

        return stats

    def draw(self, screen, camera):
        super(Creature, self).draw(screen, camera)
        if self.selected:
            vision_cone = self.vision_cone
            self.vision_cone.draw(screen, camera)
            # def __init__(self, shape, x=0, y=0, heading=0.0, color=WHITE, draw_width=0):
            x, y, w, h = vision_cone.get_bounds()
            shape = [[x, y], [x+w, y], [x+w, y+h], [x, y+h]]
            onscreen_shape_coords = [camera.scale(point) for point in shape]
            # draw.polygon(screen, WHITE, onscreen_shape_coords, 1)

            for scene_object in self.vision_cone.current_collisions:
                draw.circle(screen, RED, [int(num) for num in camera.scale(scene_object.absolute_position)], 50, 1)

    def on_collide_enter(self, other):
        # if other is a food
        if isinstance(other, Food):
            other.eaten = True

            self.health = min(self.MAX_HEALTH, self.health + other.food_value)

    def on_collide_exit(self, other):
        pass


class Food(Polygon):
    """
        Object representing the food on screen
    """
    BASE_SHAPE = [[-20, -20], [20, -20], [20, 20], [-20, 20]]

    # How much health is given when the food is eaten
    FOOD_VALUE = 30

    def __init__(self, x=0, y=0, heading=0.0, color=WHITE):
        super(Food, self).__init__(self.BASE_SHAPE, x, y, heading, color)
        self.eaten = False

        self.food_value = self.FOOD_VALUE


class VisionCone(Polygon):
    """
        A triangle for the creatures' vision
    """
    BASE_SHAPE = [[-10, 0], [30, -15], [30, 15]]

    def __init__(self, x=0, y=0, heading=0.0, color=WHITE):
        factor = 10
        
        # Scale the shape according to 'factor'
        scaled_shape = [[xpos*factor, ypos*factor] for xpos, ypos in self.BASE_SHAPE]

        x_mean = sum(point[0] for point in scaled_shape) / len(scaled_shape)
        y_mean = sum(point[1] for point in scaled_shape) / len(scaled_shape)

        scaled_centered_shape = [[xpos - x_mean, ypos - y_mean] for xpos, ypos, in scaled_shape]

        super(VisionCone, self).__init__(scaled_centered_shape, x, y, heading, color, 1)

    def on_collide_enter(self, other):
        # if other is a food, increment food counter
        if isinstance(other, Food):
            self.parent.food_seen += 1

    def on_collide_exit(self, other):
        # if other is a food, decrement food counter
        if isinstance(other, Food):
            self.parent.food_seen -= 1



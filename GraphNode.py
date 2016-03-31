from operator import add
import numpy as np
from PygameUtils import rotate_around
from math import pi
from math import cos
from math import sin
from collections import namedtuple

Event = namedtuple('Event', 'function, parameters')

two_pi = 2*pi

class GraphNode(object):
    """
        A node in the scene graph.
        Handles drawing itself to the screen as well as other related functions
    """
    def __init__(self, x=0.0, y=0.0, heading=pi/2.0):
        super().__init__()

        # Reference to parent GraphNode
        self.parent = None
        # x, y, and heading are relative to the parent
        self.position = [x, y]
        self.heading = heading

        # Hold values for the absolute position
        self.absolute_position = [0.0, 0.0]
        self.unrotated_position = [0.0, 0.0]

        # sin and cos of the heading will be cached so children don't have to recalculate
        self.cos_radians = cos(self.heading)
        self.sin_radians = sin(self.heading)

        # Used for anything that's important if this object has been selected
        self.selected = False

        self.current_collisions = set()
        self.previous_collisions = set()
        self.in_collision_phase = False

    def __repr__(self):
        return "{} at {}, {}".format(self.__class__.__name__, round(self.position[0], 0), round(self.position[1], 0))

    def do_everyframe_action(self, time_dt, game_speed):
        pass

    def start_frame(self):
        pass

    def end_frame(self):
        pass

    def update_position(self):
        """Updates the absolute_positions of this object"""
        self.calc_absolute_position()

    def draw(self, screen, camera):
        """Abtract method"""
        pass

    def move_forward(self, x_change=0, y_change=0):
        self.position[0] += x_change
        self.position[1] += y_change
        self.position_changed = True

    def move_forward(self, change):
        self.position[0] = change * self.cos_radians + self.position[0]
        self.position[1] = change * self.sin_radians + self.position[1]
        self.position_changed = True

    def rotate(self, angle_change):
        """Rotates object by angle_change radians"""
        self.heading += angle_change
        if self.heading > two_pi:
            self.heading -= two_pi
        if self.heading < 0:
            self.heading += two_pi
            
        # Cache sin and cos for use by self and children
        self.cos_radians = cos(self.heading)
        self.sin_radians = sin(self.heading)

        self.position_changed = True

    def set_position(self, position):
        self.position = position
        self.position_changed = True

    def get_absolute_position(self):
        return self.absolute_position[:]

    def set_heading(self, heading):
        self.heading = heading
        self.position_changed = True

    def calc_absolute_position(self):
        """
            This function no longer rotates based off of a parent
            That's handled in the SceneGraph.

            This should be removed or something
        """
        self.absolute_position[0] = self.position[0]
        self.absolute_position[1] = self.position[1]

    def get_bounds(self):
        return (self.absolute_position[0], self.absolute_position[1], 1, 1)

    def collide_point_bounds(self, point):
        """Returns true if point is in this objects bounding box"""
        x, y, w, h = self.get_bounds()

        px, py = point

        return px >= x and px <= x + w and py >= y and py <= y + h

    def on_collide(self, other):
        """Should be called any frame that there is a collision"""

        # Checks to see if this is the first collision event recieved this frame
        if not self.in_collision_phase:
            self.previous_collisions = self.current_collisions.copy()
            self.current_collisions = set()
            self.in_collision_phase = True

        self.current_collisions.add(other)

        if other not in self.previous_collisions:
            self.on_collide_enter(other)

    def finish_collisions(self):
        """
            Triggers on_collide_exit for each of the items that were colliding
            last frame but aren't anymore

            Should be called after all collision detection has happened
        """
        for scene_object in self.previous_collisions:
            if scene_object not in self.current_collisions:
                self.on_collide_exit(scene_object)

        self.in_collision_phase = False

    def on_collide_enter(self, other):
        """
            Abstract Base Method
            Should only be called by on_collide the first time there is a collision'
        """
        pass

    def on_collide_exit(self, other):
        """
            Abstract Base Method
            Should be called when there was a collision last frame, but not this frame
        """
        pass
            

from blist import blist
from operator import add
import numpy as np
from PygameUtils import rotate_around
from math import pi
from math import cos
from math import sin

NP_FLOAT = np.float


class GraphNode(object):
    """
        A node in the scene graph.
        Handles drawing itself to the screen as well as other related functions
    """
    def __init__(self, x=0.0, y=0.0, heading=pi/2.0):
        super(GraphNode, self).__init__()

        # Reference to parent GraphNode
        self.parent = None
        # x, y, and heading are relative to the parent
        self.position = [x, y]
        self.heading = heading

        # Will draw to the screen if visible
        self.visible = True

        # blist is a acts like a list but is implemented as a B+ tree
        # for fast insertions and deletions
        self.children = []

        # Hold values for the absolute position
        self.absolute_position = [0.0, 0.0, 0.0]
        self.unrotated_position = [0.0, 0.0, 0.0]
        self.offset_center = [0.0, 0.0]
        # Position changed is true if this or parents have moved since last frame
        self.position_changed = True

        # sin and cos of the heading will be cached so children don't have to recalculate
        self.cos_radians = cos(self.heading)
        self.sin_radians = sin(self.heading)

    def __repr__(self):
        return "{} at {}, {}".format(self.__class__.__name__, round(self.position[0], 0), round(self.position[1], 0))
        
    def reparent_to(self, new_parent):
        if self.parent:
            self.parent.remove_child(self)
        self.parent = new_parent
        self.parent.add_child(self)

    def add_child(self, new_child):
        if not issubclass(type(new_child), GraphNode):
            raise Exception("Child must subclass GraphNode")
        self.children.append(new_child)

    def remove_child(self, child):
        if not issubclass(type(child), GraphNode):
            raise Exception("Child must subclass GraphNode")
        self.children.remove(child)

    def draw(self, screen, window):
        if self.has_moved():
            self.calc_absolute_position()
        if self.visible:
            self.draw_self(screen, window)
        self.draw_children(screen, window)
        self.position_changed = False

    def draw_self(self, screen, window):
        """Abtract method"""
        pass

    def draw_children(self, screen, window):
        for child in self.children:
            child.draw(screen, window)

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
        two_pi = 2*pi
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

    def set_heading(self, heading):
        self.heading = heading
        self.position_changed = True

    def calc_absolute_position(self):
        """Offsets and rotates our position and stores it in self.absolute_position"""
        # Inlining it like this is ugly but faster
        self.unrotated_position[0] = self.position[0]
        self.unrotated_position[1] = self.position[1]

        parent = self.parent
        if parent:
            parent_position = parent.absolute_position
            self.unrotated_position[0] += parent_position[0]
            self.unrotated_position[1] += parent_position[1]
            # Rotate around parent's absolute_position
            self.absolute_position = rotate_around(parent.cos_radians, parent.sin_radians, self.unrotated_position, parent.absolute_position, parent.heading)
        else:
            self.absolute_position[0] = self.position[0]
            self.absolute_position[1] = self.position[1]

    def has_moved(self):
        if self.position_changed:
            return True
        if self.parent:
            self.position_changed |= self.parent.has_moved()
            return self.position_changed
        else:
            return False

    def get_bounds(self):
        return (self.absolute_position[0], self.absolute_position[1], 1, 1)

    def collide_point(self, point):
        """Returns true if point is in this objects bounding box"""
        x, y, w, h = self.get_bounds()

        px, py = point

        return px >= x and px <= x + w and py >= y and py <= y + h
            

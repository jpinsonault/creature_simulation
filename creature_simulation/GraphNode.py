from operator import add
import numpy as np
from PygameUtils import rotate_around
from math import pi
from math import cos
from math import sin
from collections import namedtuple

NP_FLOAT = np.float

Event = namedtuple('Event', 'function, parameters')

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
        self.absolute_position = [0.0, 0.0]
        self.unrotated_position = [0.0, 0.0]
        # Position changed is true if this or parents have moved since last frame
        self.position_changed = True

        # sin and cos of the heading will be cached so children don't have to recalculate
        self.cos_radians = cos(self.heading)
        self.sin_radians = sin(self.heading)

        # Used for random debugging purposes
        self.debug = False
        
        # Used for anything that's important if this object has been selected
        self.selected = False

        self.current_collisions = set()
        self.previous_collisions = set()
        self.in_collision_phase = False

        # Events to do 
        self.events = []

    def __repr__(self):
        return "{} at {}, {}".format(self.__class__.__name__, round(self.position[0], 0), round(self.position[1], 0))

    def add_event(self, function, params):
        self.events.append(Event(function, params))

    def handle_events(self, time_dt):
        for function, parameters in self.events:
            function(parameters)
        for child in self.children:
            child.handle_events(time_dt)

        self.do_everyframe_action(time_dt)

    def do_everyframe_action(self, time_dt):
        pass

    def start_frame(self):
        pass

    def end_frame(self):
        for child in self.children:
            child.end_frame()
        
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
        if child in self.children:
            self.children.remove(child)
        for a_child in self.children:
            a_child.remove_child(child)

    def update_position(self):
        """Updates the absolute_positions of this object and it's children"""
        if self.has_moved():
            self.calc_absolute_position()
        self.update_children()
        self.position_changed = False

    def draw(self, screen, camera):
        """Abtract method"""
        pass

    def update_children(self):
        for child in self.children:
            child.update_position()

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

    def get_absolute_position(self):
        return self.absolute_position[:]

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

    def collide_point_bounds(self, point):
        """Returns true if point is in this objects bounding box"""
        x, y, w, h = self.get_bounds()

        px, py = point

        return px >= x and px <= x + w and py >= y and py <= y + h

    def on_collide(self, other):
        """Should be called any frame that there is a collision"""

        # Checkts to see if this is the first collision event recieved this frame
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

        for child in self.children:
            child.finish_collisions()

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
            

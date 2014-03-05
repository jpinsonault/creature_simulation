from blist import blist
from operator import add
import numpy
from numpy import array
from PygameUtils import rotate_around


class GraphNode(object):
    """
        A node in the scene graph.
        Handles drawing itself to the screen as well as other related functions
    """
    def __init__(self, x=0, y=0, heading=0.0):
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
        # Stale is true if the absolute position hasn't been calculated yet
        self.stale = True
        # Position changed is true if this or parents have moved since last frame
        self.position_changed = True
        
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
        self.calc_absolute_position()
        self.position_changed = False
        if self.visible:
            self.draw_self(screen, window)
        self.draw_children(screen, window)
        self.stale = True

    def draw_self(self, screen, window):
        raise Exception("Method not implemented")

    def draw_children(self, screen, window):
        for child in self.children:
            child.draw(screen, window)

    def move(self, x_change=0, y_change=0):
        self.position[0] += x_change
        self.position[1] += y_change
        self.position_changed = True

    def rotate(self, angle_change):
        """Rotates object by angle_change degrees"""
        self.heading += angle_change
        self.position_changed = True

    def set_position(self, x, y):
        self.position = [x, y]
        self.position_changed = True

    def set_heading(self, heading):
        self.heading = heading
        self.position_changed = True

    def calc_absolute_position(self):
        """Calculates the offset for the x-y axes and heading based on the parents"""
        if self.stale:
            # Inlining it like this is ugly but faster
            if self.has_moved():
                self.unrotated_position[0] = self.position[0]
                self.unrotated_position[1] = self.position[1]

                if self.parent:
                    parent_position = self.parent.absolute_position
                    self.unrotated_position[0] += parent_position[0]
                    self.unrotated_position[1] += parent_position[1]
                    # Rotate around parent's absolute_position
                    self.absolute_position = rotate_around(self.unrotated_position, self.parent.absolute_position, self.parent.heading)

            self.stale = False


    def has_moved(self):
        if self.parent:
            return self.position_changed or self.parent.has_moved()
        else:
            return self.position_changed
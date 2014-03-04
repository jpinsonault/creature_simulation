from blist import blist
from operator import add
import numpy
from numpy import array


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
        self.x = x
        self.y = y
        self.heading = heading
        self.center = self.find_center()

        # Will draw to the screen if visible
        self.visible = True

        # blist is a acts like a list but is implemented as a B+ tree
        # for fast insertions and deletions
        self.children = []

        # Hold values for the relative position
        self._relative_position = [0.0, 0.0, 0.0]
        self.offset_center = [0.0, 0.0]
        # Stale is true if the relative position hasn't been calculated yet
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
        if self.visible:
            self.draw_self(screen, window)
        self.draw_children(screen, window)
        self.stale = True
        self.position_changed = False

    def draw_self(self, screen, window):
        raise Exception("Method not implemented")

    def draw_children(self, screen, window):
        for child in self.children:
            child.draw(screen, window)

    def move(self, x_change=0, y_change=0):
        self.x += x_change
        self.y += y_change
        self.position_changed = True

    def rotate(self, angle_change):
        """Rotates object by angle_change degrees"""
        self.heading += angle_change
        self.position_changed = True

    def set_position(self, x, y):
        self.x = x
        self.y = y
        self.position_changed = True

    def set_heading(self, heading):
        self.heading = heading
        self.position_changed = True

    def set_relative_position(self):
        """Calculates the offset for the x-y axes and heading based on the parents"""
        # Inlining it like this is ugly but faster with python arrays
        # Haven't tried array addition with numpy arrays yet
        if self.has_moved():
            # self._relative_position = [self.x, self.y, self.heading]
            self._relative_position[0] = self.x
            self._relative_position[1] = self.y
            self._relative_position[2] = self.heading

            if self.parent:
                parent_position = self.parent.relative_position()
                self._relative_position[0] += parent_position[0]
                self._relative_position[1] += parent_position[1]
                self._relative_position[2] += parent_position[2]

    def relative_position(self):
        if self.stale:
            self.set_relative_position()
            self.stale = False
        return self._relative_position

    def find_center(self):
        return [self.x, self.y]

    def has_moved(self):
        if self.parent:
            return self.position_changed or self.parent.has_moved()
        else:
            return self.position_changed
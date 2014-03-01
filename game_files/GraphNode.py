from blist import blist

class GraphNode(object):
    """
        A node in the scene graph.
        Handles drawing itself to the screen as well as other related functions
    """
    def __init__(self, parent=None, x=0, y=0, heading=0.0):
        super(GraphNode, self).__init__()

        # Reference to parent GraphNode
        self.parent = None
        # x, y, and heading are relative to the parent
        self.x = x
        self.y = y
        self.heading = heading

        # Will draw to the screen if visible
        self.visible = True

        # blist is a acts like a list but is implemented as a B+ tree
        # for fast insertions and deletions
        self.children = blist()
        
    def reparent_to(self, new_parent):
        if self.parent:
            self.parent.remove_child(self)
        self.parent = new_parent
        self.add_child(self)

    def add_child(self, new_child):
        self.children.append(new_child)

    def remove_child(self, child):
        self.children.remove(child)

    def draw(self, screen, window):
        self.draw_self(screen, window)
        self.draw_children(screen, window)

    def draw_self(self, screen, window):
        raise Exception("Method not implemented")

    def draw_children(self, screen, window):
        for child in self.children:
            child.draw(screen, window)

    def move(self, x_change=0, y_change=0):
        self.x += x_change
        self.y += y_change

    def rotate(angle_change):
        """Rotates object by angle_change degrees"""
        self.heading += angle_change

    def set_position(self, x, y):
        self.x = x
        self.y = y

    def set_heading(self, heading):
        self.heading = heading
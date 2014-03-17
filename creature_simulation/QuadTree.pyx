import pygame
import pdb
import sys
from pprint import pprint


class QuadTree(object):
    def __init__(self, bounds, int depth=15, int max_objects=4, object_map = None, parent=None):
        super(QuadTree, self).__init__()
        self.bounds = bounds
        self.depth = depth
        self.max_objects = max_objects

        self.parent = parent

        # For quick look up of nodes
        if not object_map:
            self.object_map = {}
        else:
            self.object_map = object_map

        self.scene_objects = []
        self.nodes = None

    def insert(self, new_object):
        scene_objects = self.scene_objects

        # check if node was subdivided
        if self.nodes:
            # if yes check if objects fits any of the subnodes
            node = self.get_subnode_for_bounds(new_object.get_bounds())
            if node:
                # if it fits one of subnodes add it to this subnode
                node.insert(new_object)
            else:
                # else append it to the objects held by this node
                scene_objects.append(new_object)
                # Point the new object to this node
                self.object_map[new_object] = self
            return

        # if it wasn't subdivided add the object to this node
        scene_objects.append(new_object)
        # Point the new object to this node
        self.object_map[new_object] = self

        # check if adding object didn't append it past max objects before subdividing and if it isn't max depth of the tree
        if len(scene_objects) > self.max_objects and self.depth >= 0:
            # if it did subdivide the node
            self.subdivide()
            # clear the reference to the  array of object bound to this node - reference to these objects is stored in `objects` array
            self.scene_objects = []


            # iterate over all the objects and try to put them inside subnodes they fit in
            for scene_object in scene_objects:
                subnode = self.get_subnode_for_bounds(scene_object.get_bounds())

                if (subnode):
                    subnode.insert(scene_object)
                else:
                    self.scene_objects.append(scene_object)

    def insert_objects(self, scene_objects):
        for scene_object in scene_objects:
            self.insert(scene_object)

    def update_objects(self, scene_objects):
        for scene_object in scene_objects:
            self.update(scene_object)

    def update(self, update_object, object_node = None):
        # Find node object is located in
        # print("Updating {}, length of object_map: {}".format(id(update_object), len(self.object_map)))
        if not object_node:
            try:
                object_node = self.object_map[update_object]
            except KeyError:
                # Scene_object isn't in the quadtree for some reason
                return
        bounds = update_object.get_bounds()
        object_node.update_to_self(update_object, bounds)

    def update_to_self(self, update_object, target_bounds):
        # If it fits in this node
        if self.fits(target_bounds):
            # If we have subnodes and it fits in a subnode
            if self.nodes:
                subnode = self.get_subnode_for_bounds(target_bounds)
                if subnode:
                    # Move to a new sub node
                    # Remove from self one and insert into the subnode
                    self.remove(update_object)
                    subnode.insert(update_object)
                else:
                    # We have subnodes but it doesn't fit in them.
                    # Insert into this node
                    if update_object not in self.scene_objects:
                        self.remove(update_object)
                        self.scene_objects.append(update_object)
                        self.object_map[update_object] = self
            else:
                if update_object not in self.scene_objects:
                    # Add it to this node
                    self.remove(update_object)
                    self.scene_objects.append(update_object)
                    self.object_map[update_object] = self

        else:
            if self.parent:
                # Moved to a parent node
                self.parent.update_to_self(update_object, target_bounds)
            else:
                self.remove(update_object)

    def fits(self, target_bounds):
        cdef int bx = self.bounds[0]
        cdef int by = self.bounds[1]
        cdef int bw = self.bounds[2]
        cdef int bh = self.bounds[3]

        cdef int tx = target_bounds[0]
        cdef int ty = target_bounds[1]
        cdef int tw = target_bounds[2]
        cdef int th = target_bounds[3]

        # If the top left and bottom right fit, it fits
        return tx >= bx and ty >= by and tx + tw <= bx + bw and ty + th <= by + bh

    def remove_objects(self, scene_objects):
        for scene_object in scene_objects:
            self.remove(scene_object)

    def remove(self, remove_object):
        object_node = self.object_map[remove_object]
        # Remove from the node it's in
        object_node.remove_from_node(remove_object)
        # Make the object_map no longer point to the old node
        del self.object_map[remove_object]

    def remove_from_node(self, remove_object):
        self.scene_objects.remove(remove_object)

    def trim_empty_nodes(self):
        """
            Returns true if parent should delete it's nodes
        """
        if self.nodes:
            # If all subnodes are empty
            if all([subnode.trim_empty_nodes() for subnode in self.nodes]):
                self.nodes = None
            else:
                # Return false if any of the children's children have scene_objects left
                return False
        else:
            # We're at a leaf node now
            if not self.scene_objects:
                # Delete me
                return True
            else:
                # Don't delete me
                return False

    def subdivide(self):
        bounds = self.bounds
        x = bounds[0]
        y = bounds[1]
        width = bounds[2]
        height = bounds[3]
        half_width = width / 2.0
        half_height = height / 2.0
        max_objects = self.max_objects
        cdef int depth = self.depth - 1
        nodes = []

        self.nodes = nodes

        # create four subnodes
        # top left
        nodes.append(QuadTree((
            x,
            y,
            half_width,
            half_height
        ), depth, max_objects, self.object_map, self))
        
        # top right
        nodes.append(QuadTree((
            x + half_width,
            y,
            half_width,
            half_height
        ), depth, max_objects, self.object_map, self))
        
        # bottom left
        nodes.append(QuadTree((
            x,
            y + half_height,
            half_width,
            half_height
        ), depth, max_objects, self.object_map, self))
        
        # bottom right
        nodes.append(QuadTree((
            x + half_width,
            y + half_height,
            half_width,
            half_height
        ), depth, max_objects, self.object_map, self))

    def get_subnode_for_bounds(self, target_bounds):
        bounds = self.bounds
        # cdef int bx, by, bw, bh = bounds
        cdef float bx = bounds[0]
        cdef float by = bounds[1]
        cdef float bw = bounds[2]
        cdef float bh = bounds[3]

        cdef float bh_half = bh / 2.0
        cdef float bw_half = bw / 2.0

        cdef float bx2 = bx + bw
        cdef float by2 = by + bh
        # cdef float tx, ty, tw, th = target_bounds
        cdef float tx = target_bounds[0]
        cdef float ty = target_bounds[1]
        cdef float tw = target_bounds[2]
        cdef float th = target_bounds[3]
        cdef float tx2 = tx + tw
        cdef float ty2 = ty + th

        # if either target bound's width or height is larger then half of node's width or height it means target bounds won't fit any subnode
        if tw > bw_half or th > bh_half:
            return None
        # check if it fits top left node
        elif tx >= bx and ty >= by and tx2 <= bx + bw_half and ty2 <= by + bh_half:
            return self.nodes[0]
        # check if it fits top right node
        elif tx >= bx + bw_half and ty >= by and tx2 <= bx2 and ty2 <= by + bh_half:
            return self.nodes[1]
        # check if it fits bottom left node
        elif tx >= bx and ty >= by + bh_half and tx2 <= bx + bw_half and ty2 <= by2:
            return self.nodes[2]
        # check if it fits bottom right node
        elif tx >= bx + bw_half and ty >= by + bh_half and tx2 <= bx2 and ty2 <= by2:
            return self.nodes[3]
        
        # otherwise it means target bounds overlap more then one subnode and it needs to be added to this node
        return None

    def ray_cast(self, point):
        """Given a point, return the first object found that it intersects with"""

        # First pass gets the objects from the tree
        first_pass_objects = self.get_objects_at_bounds((point[0], point[1], 0, 0))

        second_pass_objects = []
        # Second does a simple check against the bounding box of the object
        if first_pass_objects:
            second_pass_objects = [scene_object for scene_object in first_pass_objects if scene_object.collide_point_bounds(point)]

        # Third pass compares against the object's actual shape
        hits = []
        if second_pass_objects:
            hits = [scene_object for scene_object in first_pass_objects if scene_object.collide_point_poly(point)]

        if hits:
            return hits[0]
        else:
            return None

    def get_objects_at_bounds(self, target_bounds):

        nodes = self.nodes
        if not nodes and not self.scene_objects:
            return None
        
        bounds = self.bounds
        cdef float bx = bounds[0]
        cdef float by = bounds[1]
        cdef float bw = bounds[2]
        cdef float bh = bounds[3]
        cdef float bx2 = bx + bw
        cdef float by2 = by + bh

        cdef float tx = target_bounds[0]
        cdef float ty = target_bounds[1]
        cdef float tw = target_bounds[2]
        cdef float th = target_bounds[3]
        cdef float tx2 = tx + tw
        cdef float ty2 = ty + th

        # check if node doesn't intersect with target bounds - if it doesn't return None
        if (tx >= bx2 or ty >= by2 or tx2 <= bx or ty2 <= by):
            return None
        

        # if the node is fully overlaped by bounds then add all its objects and all objects which are held by subnodes and their subnodes
        if (tx <= bx and ty <= by and tx2 >= bx2 and ty2 >= by2):
            return self.get_all_objects()
        

        # if its in bounds add all the objects from self node to potentially intersecting objects array
        found_objects = self.scene_objects[:]

        # if node has subnodes check them recursively for potentially intersecting objects
        if nodes:
            subnode_objects = nodes[0].get_objects_at_bounds(target_bounds)
            if subnode_objects:
                found_objects += subnode_objects
            
            subnode_objects = nodes[1].get_objects_at_bounds(target_bounds)
            if subnode_objects:
                found_objects += subnode_objects
            
            subnode_objects = nodes[2].get_objects_at_bounds(target_bounds)
            if subnode_objects:
                found_objects += subnode_objects
            
            subnode_objects = nodes[3].get_objects_at_bounds(target_bounds)
            if subnode_objects:
                found_objects += subnode_objects
            
        
        if found_objects:
            return found_objects
        
        return None

    def get_nodes_at_bounds(self, target_bounds):
        """
            Returns all of the nodes at the bounds, good for drawing the tree
        """
        nodes = self.nodes
        if not nodes:
            return None

        bounds = self.bounds
        cdef float bx = bounds[0]
        cdef float by = bounds[1]
        cdef float bw = bounds[2]
        cdef float bh = bounds[3]
        cdef float bx2 = bx + bw
        cdef float by2 = by + bh
        # cdef float tx, ty, tx2, ty2 = target_bounds
        cdef float tx = target_bounds[0]
        cdef float ty = target_bounds[1]
        cdef float tw = target_bounds[2]
        cdef float th = target_bounds[3]
        cdef float tx2 = tx + tw
        cdef float ty2 = ty + th

        # check if node doesn't intersect with target bounds - if it doesn't return None
        if (tx >= bx2 or ty >= by2 or tx2 <= bx or ty2 <= by):
            return None
        
        # if the node is fully overlaped by bounds then add all its objects and all objects which are held by subnodes and their subnodes
        if (tx <= bx and ty <= by and tx2 >= bx2 and ty2 >= by2):
            return self.get_all_nodes()
        

        # if its in bounds add all the nodes from this node to potentially intersecting nodes array
        found_nodes = self.nodes[:]

        # if node has subnodes check them recursively for potentially intersecting objects
        if nodes:
            subnodes = nodes[0].get_nodes_at_bounds(target_bounds)
            if subnodes:
                found_nodes += subnodes
            
            subnodes = nodes[1].get_nodes_at_bounds(target_bounds)
            if subnodes:
                found_nodes += subnodes
            
            subnodes = nodes[2].get_nodes_at_bounds(target_bounds)
            if subnodes:
                found_nodes += subnodes
            
            subnodes = nodes[3].get_nodes_at_bounds(target_bounds)
            if subnodes:
                found_nodes += subnodes
            
        
        if found_nodes:
            return found_nodes
        
        return None

    def get_all_objects(self):
        found_objects = self.scene_objects[:]

        # check if node has subnodes
        if self.nodes:
            nodes = self.nodes
            # if yes recursively get all objects held by its subnodes and their subnodes
            subnode_objects = nodes[0].get_all_objects()
            if subnode_objects:
                found_objects += subnode_objects
            
            subnode_objects = nodes[1].get_all_objects()
            if subnode_objects:
                found_objects += subnode_objects
            
            subnode_objects = nodes[2].get_all_objects()
            if subnode_objects:
                found_objects += subnode_objects
            
            subnode_objects = nodes[3].get_all_objects()
            if subnode_objects:
                found_objects += subnode_objects

        return found_objects

    def get_all_nodes(self):
        if not self.nodes:
            return None
        
        found_nodes = self.nodes[:]

        # check if node has subnodes
        if self.nodes:
            nodes = self.nodes
            # if yes recursively get all nodes held by its subnodes and their subnodes
            subnodes = nodes[0].get_all_nodes()
            if subnodes:
                found_nodes += subnodes
            
            subnodes = nodes[1].get_all_nodes()
            if subnodes:
                found_nodes += subnodes
            
            subnodes = nodes[2].get_all_nodes()
            if subnodes:
                found_nodes += subnodes
            
            subnodes = nodes[3].get_all_nodes()
            if subnodes:
                found_nodes += subnodes

        return found_nodes

    def wipe(self):
        if self.nodes:
            nodes = self.nodes
            nodes[0].wipe()
            nodes[1].wipe()
            nodes[2].wipe()
            nodes[3].wipe()
        
        self.scene_objects = []
        self.nodes = None

    def print_tree(self, depth=0):
        """Recursively print the tree"""
        def print_(depth, string):
            print "{}{}".format('  ' * depth, string)

        num_items = len(self.scene_objects)
        print_(depth, "Level {}: {} scene_objects".format(depth, num_items))

        if self.nodes:
            # top left node
            print_(depth, "Top Left:")
            self.nodes[0].print_tree(depth + 1)
            # top right node
            print_(depth, "Top Right:")
            self.nodes[1].print_tree(depth + 1)
            # bottom left node
            print_(depth, "Bottom Left:")
            self.nodes[2].print_tree(depth + 1)
            # bottom right node
            print_(depth, "Bottom Right:")
            self.nodes[3].print_tree(depth + 1)


    def draw_tree(self, screen, camera):
        """Draws the bounds of all the nodes to the screen"""
        visible_nodes = self.get_nodes_at_bounds(camera.get_bounds())
        # visible_nodes = self.get_all_nodes()

        if visible_nodes:
            for node in visible_nodes:
                scaled_rect = camera.scale_rect(node.bounds)
                pygame.draw.rect(screen, (0, 255, 0), scaled_rect, 1)

    count = 0
    def get_all_collisions(self):
        """
            Look through the whole tree and return a list of lists of all the possible collisions
            Starts at the root and goes down to each leaf node, recurring back up, passing up the 
                collisions
        """

        self.count += 1

        cdef int index
        nodes = self.nodes

        collisions = []

        if nodes:
            # Look in subnodes for scene objects
            for index in range(4):
                # Combine this node's scene_objects with the nodes from the children
                sub_collisions = nodes[index].get_all_collisions()
                # pprint(sub_collisions)
                # sys.exit()
                if sub_collisions:
                    # If a list of lists
                    if type(sub_collisions[0]) == list:
                        for sub_collision in sub_collisions:
                            collisions.append(self.scene_objects + sub_collision)
                    else:
                        collisions.append(self.scene_objects + sub_collisions)

            # print("Collisions:")
            # pprint(collisions)
            # print("")
        else:
            collisions = self.scene_objects[:]

        return collisions

        

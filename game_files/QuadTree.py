import pdb
import pygame


class QuadTree(object):
    def __init__(self, bounds, depth=7, max_objects=2, object_map = None, parent=None):
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

            subnode = None

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

        self.trim_empty_nodes()

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
                    # Remove from self one and insert into the subnode
                    self.remove(update_object)
                    subnode.insert(update_object)
                    # print("Moved to a new sub node")
            # else it hasn't changed node, we're done
        else:
            if self.parent:
                # Moved to a parent node"
                self.parent.update_to_self(update_object, target_bounds)
            else:
                self.remove(update_object)

    def fits(self, target_bounds):
        bx, by, bw, bh = self.bounds
        tx, ty, tw, th = target_bounds

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
        depth = self.depth - 1
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
        bx, by, bw, bh = bounds
        bh_half = bh / 2.0
        bw_half = bw / 2.0
        # by = bounds[1]
        # bw = bounds[2]
        # bh = bounds[3]
        bx2 = bx + bw
        by2 = by + bh
        tx, ty, tw, th = target_bounds
        # ty = target_bounds[1]
        # tw = target_bounds[2]
        # th = target_bounds[3]
        tx2 = tx + tw
        ty2 = ty + th

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

    def get_objects_at_bounds(self, target_bounds):

        nodes = self.nodes
        if not nodes and not self.scene_objects:
            return None
        
        bounds = self.bounds
        # bx, by, bx2, by2 = bounds
        bx, by, bw, bh = bounds
        # by = bounds[1]
        bx2 = bx + bw
        by2 = by + bh
        # tx, ty, tx2, ty2 = target_bounds
        tx, ty, tw, th = target_bounds
        # ty = target_bounds[1]
        tx2 = tx + tw
        ty2 = ty + th

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
        # bx, by, bx2, by2 = bounds
        bx, by, bw, bh = bounds
        # by = bounds[1]
        bx2 = bx + bw
        by2 = by + bh
        # tx, ty, tx2, ty2 = target_bounds
        tx, ty, tw, th = target_bounds
        # ty = target_bounds[1]
        tx2 = tx + tw
        ty2 = ty + th

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



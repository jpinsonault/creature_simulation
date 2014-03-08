import pdb

class QuadTree(object):
    def __init__(self, bounds, depth=8, max_objects=4):
        super(QuadTree, self).__init__()
        self.bounds = bounds
        self.depth = depth
        self.max_objects = max_objects

        self.scene_objects = []
        self.nodes = None

    def insert(self, new_object):
        scene_objects = self.scene_objects

        # check if node was subdivided
        if self.nodes:
            # if yes check if objects fits any of the subnodes
            node = self.get_subnode_for_bounds(new_object.bounds)
            if node:
                # if it fits one of subnodes add it to this subnode
                node.insert(new_object)
            else:
                # else append it to the objects held by this node
                scene_objects.append(new_object)
            return

        # if it wasn't subdivided add the object to this node
        scene_objects.append(new_object)

        # check if adding object didn't append it past max objects before subdividing and if it isn't max depth of the tree
        if len(scene_objects) > self.max_objects and self.depth >= 0:
            # if it did subdivide the node
            self.subdivide()
            pdb.set_trace()
            # clear the reference to the  array of object bound to this node - reference to these objects is stored in `objects` array
            self.scene_objects = []

            subnode = None

            # iterate over all the objects and try to put them inside subnodes they fit in
            for scene_object in scene_objects:
                subnode = self.get_subnode_for_bounds(scene_object.bounds)

                if (subnode):
                    subnode.insert(scene_object)
                else:
                    self.scene_objects.append(scene_object)

    def insert_objects(self, scene_objects):
        for scene_object in scene_objects:
            self.insert(scene_object)

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
        ), depth, max_objects))
        
        # top right
        nodes.append(QuadTree((
            x + half_width,
            y,
            half_width,
            half_height
        ), depth, max_objects))
        
        # bottom left
        nodes.append(QuadTree((
            x,
            y + half_height,
            half_width,
            half_height
        ), depth, max_objects))
        
        # bottom right
        nodes.append(QuadTree((
            x + half_width,
            y + half_height,
            half_width,
            half_height
        ), depth, max_objects))

    def get_subnode_for_bounds(self, target_bounds):
        bounds = self.bounds
        bx = bounds[0]
        by = bounds[1]
        bw = bounds[2]
        bh = bounds[3]
        bx2 = bx + bw
        by2 = by + bh
        tx = target_bounds[0]
        ty = target_bounds[1]
        tw = target_bounds[2]
        th = target_bounds[3]
        tx2 = tx + tw
        ty2 = ty + th

        # if either target bound's width or height is larger then half of nodes width or height it means target bounds won't fit any subnode
        if tw > bw / 2.0 or th > bh / 2.0:
            return None
        # check if it fits top left node
        elif tx >= bx and ty >= by and tx2 <= bx + bw / 2.0 and ty2 <= by + bh / 2.0:
            return self.nodes[0]
        # check if it fits top right node
        elif tx >= bx + bw / 2.0 and ty >= by and tx2 <= bx2 and ty2 <= by + bh / 2.0:
            return self.nodes[1]
        # check if it fits bottom left node
        elif tx >= bx and ty >= by + bh / 2.0 and tx2 <= bx + bw / 2.0 and ty2 <= by2:
            return self.nodes[2]
        # check if it fits bottom right node
        elif tx >= bx + bw / 2.0 and ty >= by + bh / 2.0 and tx2 <= bx2 and ty2 <= by2:
            return self.nodes[3]
        
        # otherwise it means target bounds overlap more then one subnode and it needs to be added to this node
        return None

    def get_object_at_bounds(self, target_bounds):

        nodes = self.nodes
        if not nodes and not self.scene_objects:
            return None
        
        bounds = self.bounds
        bx = bounds[0]
        by = bounds[1]
        bx2 = bx + bounds[2]
        by2 = by + bounds[3]
        tx = target_bounds[0]
        ty = target_bounds[1]
        tx2 = tx + target_bounds[2]
        ty2 = ty + target_bounds[3]

        # check if node doesn't intersect with target bounds - if it doesn't return None
        if (not (tx >= bx and ty >= by and tx <= bx2 and ty <= by2) or
            not (tx2 >= bx and ty2 >= by and tx2 <= bx2 and ty2 <= by2) or
            not (tx <= bx2 and ty <= by2 and tx2 >= bx and ty2 >= by)):
            return None
        

        # if the node is fully overlaped by bounds then add all its objects and all objects which are held by subnodes and their subnodes
        if (tx <= bx and ty <= by and tx2 >= bx2 and ty2 >= by2):
            return self.get_all_objects()
        

        # if its in bounds add all the objects from self node to potentially intersecting objects array
        found_objects = self.scene_objects[:]

        # if node has subnodes check them recursively for potentially intersecting objects
        if nodes:
            subnode_objects = nodes[0].get_object_at_bounds(target_bounds)
            if subnode_objects:
                found_objects += subnode_objects
            
            subnode_objects = nodes[1].get_object_at_bounds(target_bounds)
            if subnode_objects:
                found_objects += subnode_objects
            
            subnode_objects = nodes[2].get_object_at_bounds(target_bounds)
            if subnode_objects:
                found_objects += subnode_objects
            
            subnode_objects = nodes[3].get_object_at_bounds(target_bounds)
            if subnode_objects:
                found_objects += subnode_objects
            
        
        if found_objects:
            return found_objects
        
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

from PygameUtils import rotate_around


def NoopTransformer(*args, **kwargs):
    """Doesn't do anything"""
    pass


def OldStyleTransformer(entity, parent_entity):
    entity.unrotated_position[0] = entity.position[0]
    entity.unrotated_position[1] = entity.position[1]

    parent_position = parent_entity.absolute_position
    # Translate the entity based on parent's position
    entity.unrotated_position[0] += parent_position[0]
    entity.unrotated_position[1] += parent_position[1]
    # Rotate around parent's absolute_position
    entity.absolute_position = rotate_around(parent_entity.cos_radians,
                                             parent_entity.sin_radians,
                                             entity.unrotated_position,
                                             parent_entity.absolute_position,
                                             parent_entity.heading)


class SceneGraph(object):
    def __init__(self):
        super().__init__()
        self.nodes = []
        self.entity_node_map = {}

    def add(self, entity):
        """Add to top level"""
        self.nodes.append(GraphNode(entity))

    def add_to_parent(self, entity, parent, transformer=NoopTransformer):
        """
            Recursively search scene graph for node containing 'parent'
            Add entity to parent
        """
        parent = self.find_node_by_entity(parent, self.nodes)
        if not parent:
            raise Exception("Node for parent entity '{}' couldn't be found!".format(entity))

        parent.add_child_entity(entity, transformer)

    def update(self):
        for node in self.nodes:
            node.update()

    def find_node_by_entity(self, entity, root_nodes=None):
        """Recursively search scene graph for node containing entity"""
        if root_nodes is None:
            root_nodes = self.nodes

        if len(root_nodes) == 0:
            return None
        for node in root_nodes:
            if node.entity == entity:
                return node
            child_search = self.find_node_by_entity(entity, node.children)

            if child_search:
                return child_search

        return None

    def remove(self, entity):
        """Find the node and remove it from it's parent if it has one"""
        node = self.find_node_by_entity(entity, self.nodes)

        if not node:
            raise Exception("Node for entity '{}' couldn't be found!".format(entity))

        if node.parent:
            node.parent.remove_child_entity(entity)
        else:
            self.nodes.remove(node)

    def __contains__(self, entity):
        return self.find_node_by_entity(entity, self.nodes) is not None


class GraphNode(object):
    def __init__(self, entity, parent=None, transformer=NoopTransformer):
        super().__init__()
        self.entity = entity
        self.parent = parent
        self.transformer = transformer
        self.children = []

    def update(self):
        """
            Transform this node, then update the children nodes recursively
        """
        if self.parent:
            self.transformer(self.entity, self.parent.entity)

        for child in self.children:
            child.update()

    def add_child_entity(self, child_entity, transformer=NoopTransformer):
        new_node = GraphNode(child_entity, parent=self, transformer=transformer)
        self.children.append(new_node)

    def find_child_by_entity(self, entity):
        """Find the first child GraphNode which contains entity, or return None"""
        return next((child for child in self.children if child.entity == entity), None)

    def remove_child_entity(self, child_entity):
        found_node = self.find_child_by_entity(child_entity)
        if found_node:
            self.children.remove(found_node)
        else:
            raise Exception("Child node for entity '{}' couldn't be found!".format(child_entity))

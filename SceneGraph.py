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
        parent = self._find_node_by_entity(parent, self.nodes)
        if not parent:
            raise Exception("Parent node couldn't be found!")

        parent.add_child_entity(entity, transformer)

    def update(self):
        for node in self.nodes:
            node.update()



    def _find_node_by_entity(self, entity, root_nodes):
        """Recursively search scene graph for node containing entity"""
        for node in root_nodes:
            if node.entity == entity:
                return node
            elif len(node.children) == 0:
                return None
            else:
                return self._find_node_by_entity(entity, node.children)



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

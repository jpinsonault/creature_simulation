from SceneGraph import GraphNode, SceneGraph

class TestGraphnode:
    def test_insertion(self):
        scene_graph = SceneGraph()

        scene_graph.add("foo")
        scene_graph.add("bar")

        assert("foo" in scene_graph)
        assert("bar" in scene_graph)
        assert("bob" not in scene_graph)

    def test_nested_insertion(self):
        scene_graph = SceneGraph()

        scene_graph.add("foo")
        scene_graph.add_to_parent("bar", "foo")

        assert("foo" in scene_graph)
        assert("bar" in scene_graph)

        # Test foo is the parent of bar
        assert(scene_graph.find_node_by_entity("bar").parent.entity == "foo")

    def test_removal(self):
        scene_graph = SceneGraph()

        scene_graph.add("foo")

        assert("foo" in scene_graph)

        scene_graph.remove("foo")

        assert("foo" not in scene_graph)

    def test_removal_of_nested_entity(self):
        scene_graph = SceneGraph()

        scene_graph.add("foo")
        scene_graph.add_to_parent("bar", "foo")

        assert("foo" in scene_graph)
        assert("bar" in scene_graph)

        scene_graph.remove("bar")

        assert("foo" in scene_graph)
        assert("bar" not in scene_graph)

    def test_removal_of_nested_entitys_parent(self):
        scene_graph = SceneGraph()

        scene_graph.add("foo")
        scene_graph.add_to_parent("bar", "foo")

        assert("foo" in scene_graph)
        assert("bar" in scene_graph)

        scene_graph.remove("foo")

        assert("foo" not in scene_graph)
        assert("bar" not in scene_graph)
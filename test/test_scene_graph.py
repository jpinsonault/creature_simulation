from SceneGraph import GraphNode, SceneGraph
import unittest


class TestGraphnode(unittest.TestCase):
    def test_insertion(self):
        scene_graph = SceneGraph()

        scene_graph.add("foo")
        scene_graph.add("bar")

        self.assertIn("foo", scene_graph)
        self.assertIn("bar", scene_graph)
        self.assertNotIn("bob", scene_graph)

    def test_nested_insertion(self):
        scene_graph = SceneGraph()

        scene_graph.add("foo")
        scene_graph.add_to_parent("bar", "foo")

        self.assertTrue("foo" in scene_graph)
        self.assertTrue("bar" in scene_graph)

        # Test foo is the parent of bar
        self.assertEqual(scene_graph.find_node_by_entity("bar").parent.entity, "foo")

    def test_removal(self):
        scene_graph = SceneGraph()
        scene_graph.add("foo")
        self.assertIn("foo", scene_graph)
        scene_graph.remove("foo")
        self.assertNotIn("foo", scene_graph)

    def test_removal_of_nested_entity(self):
        scene_graph = SceneGraph()

        scene_graph.add("foo")
        scene_graph.add_to_parent("bar", "foo")

        self.assertIn("foo", scene_graph)
        self.assertIn("bar", scene_graph)

        scene_graph.remove("bar")

        self.assertIn("foo", scene_graph)
        self.assertNotIn("bar", scene_graph)

    def test_removal_of_nested_entitys_parent(self):
        scene_graph = SceneGraph()

        scene_graph.add("foo")
        scene_graph.add_to_parent("bar", "foo")

        self.assertIn("foo", scene_graph)
        self.assertIn("bar", scene_graph)

        scene_graph.remove("foo")

        self.assertNotIn("foo", scene_graph)
        self.assertNotIn("bar", scene_graph)
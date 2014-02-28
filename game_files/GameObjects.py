"""
	Holds objects that subclass the GraphNode class
	Creatures, Food, etc
"""

from GraphNode import GraphNode


class Polygon(GraphNode):
	"""docstring for Polygon"""
	def __init__(self, screen, shape, x=0, y=0, heading=0.0, color=None):
		super(Polygon, self).__init__(screen, x, y, heading)
		self.shape = shape
		self.center = self.find_center()

	def draw(self):
		pass

	def find_center(self):
		"""Find the geometric center of the polygon"""
		pass
		


class Creature(Polygon):
	"""
		Object representing the creature on screen

	"""
	BASE_SHAPE = [[0,0], [5, -5], [10, 0], [10, 10], [5, 15], [0, 10], [0,0]]

	def __init__(self, screen, x=0, y=0, heading=0.0):
		super(Creature, self).__init__(screen, BASE_SHAPE, x, y, heading, color=None)


class Food(Polygon):
	"""
		Object representing the creature on screen

	"""
	BASE_SHAPE = [[0,0], [10, 0], [10, -10], [0, -10]]

	def __init__(self, screen, x=0, y=0, heading=0.0):
		super(Creature, self).__init__(screen, BASE_SHAPE, x, y, heading)


		

		
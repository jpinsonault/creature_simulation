


class Toggler(object):
	"""Keeps track of SceneObjects"""
	def __init__(self):
		super(Toggler, self).__init__()
		self.object_map = {}

	def set(self, scene_object, attribute, new_value):
		old_value = getattr(scene_object, attribute)
		self.object_map[scene_object] = {"attribute": attribute, "old": old_value, "new": new_value}
		setattr(scene_object, attribute, new_value)

	def toggle(self, scene_object, attribute):
		object_dict = self.object_map[scene_object]
		old_value = object_dict["old"]
		new_value = object_dict["new"]
		attribute = object_dict["attribute"]

		# Set the attribute
		setattr(scene_object, attribute, old_value)

		# Swap new with old
		object_dict["old"] = new_value
		object_dict["new"] = old_value
		
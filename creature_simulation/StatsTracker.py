from collections import defaultdict


class StatsTracker(object):
	"""Keeps track of the population statistics"""
	def __init__(self):
		super(StatsTracker, self).__init__()

		self.distribution = defaultdict(int)

		self.stats = {
			"current_best": 0,
			"all_time_best": 0,
			"average": 0,
			"top_10_percent": 0,
		}
		
	def _best(self):
		pass

	def _average(self):
		pass

	def _top_percent(self, percent=0.1):
		pass

	def update(self, creatures):
		self._clear_stats()
		stats = self.stats
		distribution = self.distribution

		for creature in creatures:
			food_eaten = creature.total_food_eaten
			stats["average"] += food_eaten
			stats["all_time_best"] = max(food_eaten, stats["all_time_best"])
			stats["current_best"] = max(food_eaten, stats["current_best"])
			distribution[food_eaten] += 1

		stats["average"] /= len(creatures)

		return self.get_stats_strings()

	def _clear_stats(self):
		for key in self.stats.iterkeys():
			if key != "all_time_best":
				self.stats[key] = 0.0

		self.distribution = defaultdict(int)

	def get_stats_strings(self):
		"""Returns a list of strings for use with the MultiLineTextBox object"""
		return ["{}: {}".format(name, value) for name, value in self.stats.iteritems()]
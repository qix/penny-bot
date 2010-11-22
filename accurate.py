import time

class accurate:
	def __init__(self):
		self.readings = []
		self.error = 5

	def reading(self, reading):
		now = time.time()
		oldreading = reading
		for x in self.readings:
			if reading > 0.5 + (x[0] - (now-x[1])):
				oldreading = (x[0] - (now-x[1]))
				self.readings = []
				break

		self.readings.append((reading,now))

	def get_mtime(self):
		if not self.readings: return 0
		now = time.time()
		return min([now-x[1] for x in self.readings])

	def check_frozen(self):
		# No readings, treat as frozen
		if not self.readings: return True

		# If we have two readings don't treat as frozen
		if len(self.readings) > 1: return False

		return False
		# Within acceptable range
		if self.get_mtime() < self.error: return False

		# Frozen lost all data
		self.readings = []
		return True

	def times(self):
		now = time.time()
		accurate = []
		for x in self.readings:
			if now-x[1] < self.error:
				break
		else:
			self.readings = []

		for x in self.readings:
			accurate.append((x[0]-(now-x[1])))
		if not accurate:
			return [99999999]
		return accurate

	def current(self):
		return min(self.times())

	def summary(self):
		accurate = self.times()
		if accurate:
			return '%.1f || %.1f || %.1f -- %d*%.1f' % (min(accurate), sum(accurate)/len(accurate), max(accurate), len(accurate), self.get_mtime())

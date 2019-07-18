from mesa import Agent

class Cell(Agent):
	# 0 not explored
	# -1 obstacle
	# -2 not to be explored, out of border of the exploration map
	# 1 exploration ongoing
	# 2 explored
	# 42 starting position
	def __init__(self, unique_id, model, pos, difficulty, explored, priority, utility):
		super().__init__(unique_id, model)
		self.pos = pos
		# difficulty of exploring. Can obtain from it the difficulty of crossing the cell
		self.difficulty = difficulty
		self.explored = explored
		self.priority = priority
		self.utility = utility
		self.wifi_covered = False
		self.wifi_bean = False
	# this agent is only used for store data and visualization, no need of step function
	def step(self):
		pass
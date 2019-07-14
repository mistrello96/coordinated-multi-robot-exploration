from mesa import Agent

class Cell(Agent):
	# 0 not explored
	# -1 obstacle
	# 1 exploration ongoing
	# 2 explored
	def __init__(self, unique_id, model, pos, traversability, difficulty, explored, priority, utility):
		super().__init__(unique_id, model)
		self.pos = pos
		self.traversability = traversability
		self.difficulty = difficulty
		self.explored = explored
		self.priority = priority
		self.utility = utility
	# this agent is only used for store data and visualization, no need of step function
	def step(self):
		pass
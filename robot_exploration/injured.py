from mesa import Agent
from .cell import Cell
import numpy as np

class Injured(Agent):
	def __init__(self, unique_id, model, pos):
		super().__init__(unique_id, model)
		self.pos = pos
		# 0 = not found
		# 1 = rescued
		self.status = 0

	def agent_get_cell(self, index):
		tmp = self.model.grid.get_cell_list_contents(index)
		cell = [obj for obj in tmp if isinstance(obj, Cell)][0]
		return cell

	def sos(self, cell):
		rand = np.random.random_sample()
		if rand > 0.99:
			cell.priority = 1
			for close_index in self.model.grid.get_neighborhood(self.pos, "moore", include_center = False, radius = 1):
				close_cell = self.agent_get_cell(close_index)
				if close_cell.explored == 0:
					close_cell.priority = 0.3

	def step(self):
		if self.status == 0:
			cell = self.agent_get_cell(self.pos)
			if cell.explored == 0 and cell.wifi_covered:
				self.sos(cell)
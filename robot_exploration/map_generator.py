from .robot import Robot
from .cell import Cell
from .injured import Injured
from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
import numpy as np
import math
import networkx as nx
import pandas as pd
import random as rnd

class Map(Model):
	def __init__(self, ncells, obstacles_dist, ninjured):
		# used in server start
		self.running = True
		self.ncells = ncells
		self.obstacles_dist = obstacles_dist
		self.ninjured = ninjured

		# grid and schedule representation
		self.grid = MultiGrid(ncells + 2, ncells + 2, torus = False)
		self.schedule = RandomActivation(self)
		# unique counter for agents 
		self.agent_counter = 1
		out_grid = {}
		out_grid["Cell"] = {}
		out_grid["Injured"] = {}
		# place a cell agent for store data and visualization on each cell of the grid
		for i in self.grid.coord_iter():
			if i[1] != 0 and i[2] != 0 and i[1] != self.ncells + 1 and i[2] != self.ncells + 1:
				rand = np.random.random_sample()
				obstacle = True if rand > self.obstacles_dist else False
				# if free
				if obstacle:
					difficulty = np.random.randint(low = 1, high = 13)
					explored = 0
					priority = 0
					utility = 1.0
				# if obstacle
				else:
					difficulty = "inf"
					explored = -1
					priority = 0
					utility = "-inf"
			else:
  				difficulty = np.random.randint(low = 1, high = 13)
  				explored = -2
  				priority = "-inf"
  				utility = "-inf"
			# place the agent in the grid
			out_grid["Cell"][i[1:]]= [self.agent_counter, i[1:], difficulty, explored, priority, utility]
			a = Cell(self.agent_counter, self, i[1:], difficulty, explored, priority, utility)
			self.schedule.add(a)
			self.grid.place_agent(a, i[1:])
			self.agent_counter += 1


		# create injured agents
		valid_coord = []
		for i in self.grid.coord_iter():
			cell = [e for e in self.grid.get_cell_list_contents(i[1:]) if isinstance(e, Cell)][0]
			if cell.explored == 0:
				valid_coord.append(cell.pos)
		for i in range(self.agent_counter, + self.agent_counter + self.ninjured):
			inj_index = rnd.choice(valid_coord)
			out_grid["Injured"][inj_index] = [i, inj_index]
			a = Injured(i, self, inj_index)
			self.schedule.add(a)
			self.grid.place_agent(a, inj_index)	
		with open('robot_exploration/maps/mymap.py', 'w') as f:
			f.writelines(["exported_map = ", str(out_grid), '\n'])
			#print(out_grid, file=f)
		

	# what the model does at each time step
	def step(self):
		pass
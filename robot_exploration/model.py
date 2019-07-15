from .robot import Robot
from .cell import Cell
from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
import numpy as np
import math
import networkx as nx

class ExplorationArea(Model):
	def __init__(self, nrobots, radar_radius, ncells, obstacles_dist, wifi_range, alpha):
		# used in server start
		self.running = True
		self.nrobots = nrobots
		self.radar_radius = radar_radius
		self.ncells = ncells
		self.obstacles_dist = obstacles_dist
		self.wifi_range = wifi_range
		self.alpha = alpha

		# grid and schedule representation
		self.grid = MultiGrid(ncells, ncells, torus = False)
		self.schedule = RandomActivation(self)
		# unique counter for agents 
		self.agent_counter = 1
		self.nobstacle = 0

		# place a cell agent for store data and visualization on each chell of the grid
		for i in self.grid.coord_iter():
			rand = np.random.random_sample()
			obstacle = True if rand > self.obstacles_dist else False
			# if free
			if obstacle:
				difficulty = np.random.randint(low = 1, high = 13)
				explored = 0
				priority = False
				utility = 1.0
			# if obstacle
			else:
				self.nobstacle += 1
				difficulty = math.inf
				explored = -1
				priority = False
				utility = -math.inf
			# place the agent in the grid
			a = Cell(self.agent_counter, self, i[1:], difficulty, explored, priority, utility)
			self.schedule.add(a)
			self.grid.place_agent(a, i[1:])
			self.agent_counter += 1
  			
  		# graph of seen cells
		self.seen_graph = nx.DiGraph()
		
		#TODO wifi representation

		# create robotic agents
		for i in range(self.agent_counter, self.nrobots + self.agent_counter):
			y = self.random.randrange(self.grid.height)
			# DP There should be a way to avoi that while, 
			# in Python there's a function which randomize an element from
			# a list; we can use that updating the list every time we place a robot
			x = 0
			# take the agent Cell in the grid cell x,y
			cell = [obj for obj in self.grid.get_cell_list_contents(tuple([x,y])) if isinstance(obj, Cell)][0]
			# do-while structure, place agents only in free cells
			# DP Moment moment moment, does do-while still exist? 
			while(cell.explored == -1):
				y = self.random.randrange(self.grid.height)
				cell = self.grid.get_cell_list_contents(tuple([x,y]))
				cell = [obj for obj in cell if isinstance(obj, Cell)][0]
			# place robotic agens in the grid
			a = Robot(i, self, tuple([x,y]), self.radar_radius)
			self.schedule.add(a)
			self.grid.place_agent(a, (x, y))
			cell.explored = 2


	# what the model does at each time step
	def step(self):
		# call step function for all of the robots in random order
		self.schedule.step()
		# compute percentage of explored over total 
		count_explored = 0
		# iterate over cells
		for i in self.grid.coord_iter():
			cell = [obj for obj in self.grid.get_cell_list_contents(i[1:]) if isinstance(obj, Cell)][0]
			if cell.explored == 2:
				count_explored += 1
		result = count_explored / (self.ncells * self.ncells - self.nobstacle)
		# if all cells have benn explored, stop the simulation
		# TODO if cells are not explorable? (trapped between obstacle) 
		if result == 1:
			print("Exploration Completed")
			print("Final step number_step funciton: " + str(self.schedule.steps)) # debug print, I'll delete it when it won't be needed anymore DP
			self.running = False
		# keep going with the exploration
		else:
			print("Step number: " + str(self.schedule.steps)) # debug print, DP
			print(result)

	def run_model(self):
		while(True):
			# search for unexplored cells
			#debug print, DP
			print("Run model function called") # DP looks like this function does not get called in when running on the server.
			keep_going = False
			for i in self.grid.coord_iter():
				cell = [obj for obj in self.grid.get_cell_list_contents(i[1:]) if isinstance(obj, Cell)][0]
				if cell.explored == 0:
					keep_going = True
			# if found, keep going the simulation
			if keep_going:
				self.step()
			# end the simulation
			else:
				self.running = False
				break
		# Looks like that in the server mod this print do not come :(
		print("Step number at the end of run model: " + str(self.schedule.steps)) # debug print, DP
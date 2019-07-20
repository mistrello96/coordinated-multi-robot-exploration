from .robot import Robot
from .cell import Cell
from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
import numpy as np
import math
import networkx as nx
import pandas as pd
import random as rnd

number_of_steps_csv = "./robot_exploration/results/number_of_steps.csv"
exploration_percentage_csv = "./robot_exploration/results/percentage_exploration_simulation_step.csv"
robot_status_csv = "./robot_exploration/results/robots_status_simulation_step.csv"

class ExplorationArea(Model):
	def __init__(self, nrobots, radar_radius, ncells, obstacles_dist, wifi_range, alpha, 
		time_csv = number_of_steps_csv, exploration_percentage_csv = exploration_percentage_csv, 
		robot_status_csv = robot_status_csv):
		# used in server start
		self.running = True
		self.nrobots = nrobots
		self.radar_radius = radar_radius
		self.ncells = ncells
		self.obstacles_dist = obstacles_dist
		self.wifi_range = wifi_range
		self.alpha = alpha

		# Data collection tools
		# it represents the sum of the difficulties of every cell
		self.total_exploration_time_required = 0
		self.dc_percentage_step = DataCollector(
			{"step": lambda m: self.get_step(m),
			 "explored": lambda m: self.get_explored(m)}
		)
		self.dc_robot_status = DataCollector(
			{"idling": lambda m: self.get_number_robots_status(m, "idling"),
			 "travelling": lambda m: self.get_number_robots_status(m, "travelling"),
			 "exploring": lambda m: self.get_number_robots_status(m, "exploring"),
			 "deploying_bean": lambda m: self.get_number_robots_status(m, "deploying_bean"),
			 "step": lambda m: self.get_step(m)}
		)
		self.time_csv = number_of_steps_csv
		self.exploration_percentage_csv = exploration_percentage_csv
		self.robot_status_csv = robot_status_csv

		# grid and schedule representation
		self.grid = MultiGrid(ncells + 2, ncells + 2, torus = False)
		self.schedule = RandomActivation(self)
		# unique counter for agents 
		self.agent_counter = 1
		self.nobstacle = 0

		# place a cell agent for store data and visualization on each cell of the grid
		for i in self.grid.coord_iter():
			if i[1] != 0 and i[2] != 0 and i[1] != self.ncells + 1 and i[2] != self.ncells + 1:
				rand = np.random.random_sample()
				obstacle = True if rand > self.obstacles_dist else False
				# if free
				if obstacle:
					difficulty = np.random.randint(low = 1, high = 13)
					self.total_exploration_time_required += difficulty
					explored = 0
					priority = 0
					utility = 1.0
				# if obstacle
				else:
					self.nobstacle += 1
					difficulty = math.inf
					explored = -1
					priority = 0
					utility = -math.inf
			else:
  				difficulty = np.random.randint(low = 1, high = 13)
  				explored = -2
  				priority = -math.inf
  				utility = -math.inf
			# place the agent in the grid
			a = Cell(self.agent_counter, self, i[1:], difficulty, explored, priority, utility)
			self.schedule.add(a)
			self.grid.place_agent(a, i[1:])
			self.agent_counter += 1

  		# graph of seen cells
		self.seen_graph = nx.DiGraph()

		'''
		legacy code
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
			while(cell.explored == -1):
				y = self.random.randrange(self.grid.height)
				cell = self.grid.get_cell_list_contents(tuple([x,y]))
				cell = [obj for obj in cell if isinstance(obj, Cell)][0]
			# place robotic agens in the grid
			a = Robot(i, self, tuple([x,y]), self.radar_radius)
			self.schedule.add(a)
			self.grid.place_agent(a, (x, y))
			cell.explored = 2
		'''

		# create robotic agents
		rnd.seed()
		row = 0
		starting_coord = []
		# data collection number of beans requested
		self.deployed_beans_at_start = 0
		# generating the list for the starting position of robots
		for c in range(self.grid.width):
			# take the agent cell
			cell = [e for e in self.grid.get_cell_list_contents(tuple([c, row])) if isinstance(e, Cell)][0]
			if cell.explored != -1:
				starting_coord.append(c)
		for i in range(self.agent_counter, self.nrobots + self.agent_counter):
			column = rnd.choice(starting_coord)
			a = Robot(i, self, tuple([column, row]), self.radar_radius)
			self.schedule.add(a)
			self.grid.place_agent(a, (column, row))
			cell = [e for e in self.grid.get_cell_list_contents(tuple([column, row])) if isinstance(e, Cell)][0]
			cell.explored = 42
			# Dove viene deployato il robot viene deployato anche un bean (uno solo)
			if not cell.wifi_bean:
				cell.wifi_bean = True
				for index in self.grid.get_neighborhood(cell.pos, "moore", include_center = False, radius = (self.wifi_range // 3)):
					# cell = self.agent_get_cell(index)
					cell = [e for e in self.grid.get_cell_list_contents(index) if isinstance(e, Cell)][0]
					cell.wifi_covered = True
				self.deployed_beans_at_start += 1
	# what the model does at each time step
	def step(self):
		# call step function for all of the robots in random order
		self.schedule.step()
		# possible call from help
		# note that we only can know from whitch bean the call comed from, so we prioritize all the cells in the bean radius
		rand = np.random.random_sample()
		found = False
		if rand > 0.999:
			print("Someone connected to wifi and asked for help")
			for bean_index in self.grid.coord_iter():
				candidate_bean = [obj for obj in self.grid.get_cell_list_contents(bean_index[1:]) if isinstance(obj, Cell)][0]
				# pick a bean
				if candidate_bean.wifi_bean:
					for covered_index in self.grid.get_neighborhood(bean_index[1:], "moore", include_center = False, radius = (self.wifi_range // 3)):
						covered_cell = [obj for obj in self.grid.get_cell_list_contents(covered_index) if isinstance(obj, Cell)][0]
						# if it has some unexolored cell, mark them as priority cell
						if covered_cell.explored == 0:
							covered_cell.priority = 1
							# stop the search of another bean that has some free cells in his radius
							found = True
				if found:
					break

		'''
		legacy code, there's a function which does this work
		# compute percentage of explored over total 
		count_explored = 0
		# iterate over cells
		for i in self.grid.coord_iter():
			cell = [obj for obj in self.grid.get_cell_list_contents(i[1:]) if isinstance(obj, Cell)][0]
			if cell.explored == 2:
				count_explored += 1
		result = count_explored / (self.ncells * self.ncells - self.nobstacle)
		'''
		result = self.get_explored(self)
		print(result)
		self.dc_percentage_step.collect(self)
		self.dc_robot_status.collect(self)
		# if all seen cells have benn explored, stop the simulation
		# we do this so if there are unreachable cells, the cannot be seen, so the simulation stops anyway
		stop = True
		for node in self.seen_graph.nodes():
			cell = [obj for obj in self.grid.get_cell_list_contents(node) if isinstance(obj, Cell)][0]
			if cell.explored == 0 or cell.explored == 1:
				stop = False
		if stop:
			print("Exploration Completed")
			print("Final step number_step funciton: " + str(self.get_step(self))) # debug print, I'll delete it when it won't be needed anymore DP
			
			# Data collection
			df = pd.read_csv(self.time_csv)
			df = df.append({"nrobots": self.nrobots, "ncells": self.ncells, 
							"steps": self.schedule.steps, 
							"beans_deployed": self.get_number_bean_deployed(self),
							"total_exploration_time_required": self.total_exploration_time_required},
							ignore_index = True)
			df.to_csv(self.time_csv, index = False)
			
			df_explored = self.dc_percentage_step.get_model_vars_dataframe()
			print(df_explored.head(6))
			df = pd.read_csv(self.exploration_percentage_csv)
			if len(df["sim_id"]) == 0: # in case the csv has no values
				df_explored["sim_id"] = 0
			else:
				df_explored["sim_id"] = df["sim_id"][df.index[-1]] + 1 # get the last value of sim_id increase of one
			df = df.append(df_explored, ignore_index = True, sort = False) # If there are some problems in the csvs, look for this sort, DP
			df.to_csv(self.exploration_percentage_csv, index = False)

			df_robots_status = self.dc_robot_status.get_model_vars_dataframe()
			print(df_robots_status.head(6))
			df = pd.read_csv(self.robot_status_csv)
			if len(df["sim_id"]) == 0:
				df_robots_status["sim_id"] = 0
			else:
				df_robots_status["sim_id"] = df["sim_id"][df.index[-1]] + 1
			df = df.append(df_robots_status, ignore_index = True, sort = False)
			df.to_csv(self.robot_status_csv, index = False)

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
			stop = True
			for node in self.seen_graph.nodes():
				cell = [obj for obj in self.grid.get_cell_list_contents(node) if isinstance(obj, Cell)][0]
				if cell.explored == 0 or cell.explored == 1:
					stop = False
			# if all seen cells have benn explored, stop the simulation
			# we do this so if there are unreachable cells, the cannot be seen, so the simulation stops anyway
			if stop:
				self.running = False
				break
			else:
				self.step()

		# Looks like that in the server mod this print do not come :(
		print("Step number at the end of run model: " + str(self.schedule.steps)) # debug print, DP

	# Data collection utilities
	@staticmethod
	def get_step(m):
		return m.schedule.steps

	@staticmethod
	def get_explored(m):
		count_explored = 0
		for i in m.grid.coord_iter():
			cell = [obj for obj in m.grid.get_cell_list_contents(i[1:]) if isinstance(obj, Cell)][0]
			if cell.explored == 2:
				count_explored += 1
		result = count_explored / (m.ncells * m.ncells - m.nobstacle)
		return result

	@staticmethod
	def get_number_robots_status(m, status):
		status_value = {"idling": 0, "travelling": 1, "exploring": 2, "deploying_bean": 3}
		return len([x for x in m.schedule.agents if isinstance(x, Robot) and x.status == status_value[status]])

	@staticmethod
	def get_number_bean_deployed(m):
		return sum([x.number_bean_deployed for x in m.schedule.agents if isinstance(x, Robot)]) + m.deployed_beans_at_start
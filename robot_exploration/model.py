from .robot import Robot
from .cell import Cell
from .injured import Injured
from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
import numpy as np
from numpy import inf # why do we import something we do not use? and which is already imported in the line before?
import math
import networkx as nx
import pandas as pd
import random as rnd
from ast import literal_eval
import sys
from scipy.spatial import distance

number_of_steps_csv = "./robot_exploration/results/number_of_steps.csv"
exploration_percentage_csv = "./robot_exploration/results/percentage_exploration_simulation_step.csv"
robot_status_csv = "./robot_exploration/results/robots_status_simulation_step.csv"
alpha_csv = "./robot_exploration/results/alpha_variation.csv"
gamma_csv = "./robot_exploration/results/gamma_variation.csv"

class ExplorationArea(Model):
	def __init__(self, nrobots, radar_radius, wifi_range, alpha, gamma, ninjured=None, ncells=None, obstacles_dist=None,
		load_file = None,
		dump_datas = True, # enable data collection
		alpha_variation = False, # record datas for alpha variation studies
		alpha_csv = alpha_csv,
		gamma_variation = False, # record datas for gamma variation studies
		gamma_csv = gamma_csv,
		optimization_task = False, # enable a small part of data collection for optimization task
		time_csv = number_of_steps_csv,
		exploration_percentage_csv = exploration_percentage_csv, 
		robot_status_csv = robot_status_csv):

		# checking params consistency
		if not load_file and (not ncells or not obstacles_dist or not ninjured):
			print("Invalid params")
			sys.exit(-1)

		# used in server start
		self.running = True
		self.nrobots = nrobots
		self.radar_radius = radar_radius
		self.ncells = ncells
		self.obstacles_dist = obstacles_dist
		self.wifi_range = wifi_range
		self.alpha = alpha
		self.gamma = gamma
		self.ninjured = ninjured
		self.dump_datas = dump_datas
		self.optimization_task = optimization_task
		self.frontier = set()
		# Data collection tools
		if self.dump_datas:
			# it represents the sum of the difficulties of every cell
			self.total_difficulty = 0
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

		if self.optimization_task:
			self.total_idling_time = 0

		self.alpha_variation = alpha_variation
		self.gamma_variation = gamma_variation
		if self.alpha_variation:
			self.costs_each_path = list()
			self.alpha_csv = alpha_csv
		if self.gamma_variation:
			self.gamma_df = pd.DataFrame(columns = ["step", "mean", "std"])
			self.gamma_csv = gamma_csv

		self.schedule = RandomActivation(self)
		# unique counter for agents 
		self.agent_counter = 1
		self.nobstacle = 0
	  	# graph of seen cells
		self.seen_graph = nx.DiGraph()

		# place a cell agent for store data and visualization on each cell of the grid
		# if map is not taken from file, create it
		if load_file == None:
			self.grid = MultiGrid(ncells + 2, ncells + 2, torus = False)
			for i in self.grid.coord_iter():
				if i[1] != 0 and i[2] != 0 and i[1] != self.ncells + 1 and i[2] != self.ncells + 1:
					rand = np.random.random_sample()
					obstacle = True if rand < self.obstacles_dist else False
					# if obstacle
					if obstacle:
						self.nobstacle += 1
						difficulty = math.inf
						explored = -1
						priority = 0
						utility = -math.inf
					# if free
					else:
						difficulty = np.random.randint(low = 1, high = 13)
						if self.dump_datas:
							self.total_difficulty += difficulty
						explored = 0
						priority = 0
						utility = 1.0
				# if contour cell
				else:
	  				difficulty = np.random.randint(low = 1, high = 13)
	  				explored = -2
	  				priority = -math.inf
	  				utility = -math.inf
				# place the agent in the grid
				a = Cell(self.agent_counter, self, i[1:], difficulty, explored, priority, utility)
				self.grid.place_agent(a, i[1:])
				self.agent_counter += 1

			# create injured agents
			valid_coord = []
			for i in self.grid.coord_iter():
				cell = [e for e in self.grid.get_cell_list_contents(i[1:]) if isinstance(e, Cell)][0]
				if cell.explored == 0:
					valid_coord.append(cell.pos)
			for i in range(0, ninjured):
				inj_index = rnd.choice(valid_coord)
				a = Injured(self.agent_counter, self, inj_index)
				self.schedule.add(a)
				self.grid.place_agent(a, inj_index)
				self.agent_counter += 1	
		else:
			# load map from file
			try:
				with open(load_file, 'r') as f:
					file = f.read()
			except:
				print("file not found")
				sys.exit(-1)
			exported_map = literal_eval(file)
			self.ncells = int(math.sqrt(len(exported_map["Cell"].keys())))
			self.grid = MultiGrid(self.ncells, self.ncells, torus = False)
			for index in exported_map["Cell"].keys():
				cell = exported_map["Cell"][index]
				difficulty = cell[2]
				explored = cell[3]
				priority = cell[4]
				utility = cell[5]
				if difficulty == "inf":
					difficulty = math.inf
				if priority == "-inf":
					priority = -math.inf
				if utility == "-inf":
					utility = -math.inf
				a = Cell(self.agent_counter, self, index, difficulty, explored, priority, utility)
				self.grid.place_agent(a, index)
				self.agent_counter += 1

			for index in exported_map["Injured"].keys():
				a = Injured(self.agent_counter, self, index)
				self.schedule.add(a)
				self.grid.place_agent(a, index)
				self.agent_counter += 1	
		
		# create robotic agents
		rnd.seed()
		row = 0
		starting_coord = []
		# data collection number of beans requested
		if self.dump_datas:
			self.deployed_beans_at_start = 0
		# generating the list for the starting position of robots
		for c in range(self.grid.width):
			# take the agent cell
			cell = [e for e in self.grid.get_cell_list_contents(tuple([c, row])) if isinstance(e, Cell)][0]
			if cell.explored != -1:
				starting_coord.append(c)
		for i in range(0, self.nrobots):
			column = rnd.choice(starting_coord)
			a = Robot(self.agent_counter, self, tuple([column, row]), self.radar_radius)
			self.schedule.add(a)
			self.grid.place_agent(a, (column, row))
			self.agent_counter += 1
			# create initial frontier: add cell in front of the robot if valid and not obstacles
			cell = [e for e in self.grid.get_cell_list_contents(tuple([column, row + 1])) if isinstance(e, Cell)][0] # maybe this list comprehension can become a function for simple reading
			if cell.explored == 0:
				self.frontier.add(tuple([column, row +  1]))
			try:
				cell = [e for e in self.grid.get_cell_list_contents(tuple([column + 1, row + 1])) if isinstance(e, Cell)][0]
				if cell.explored == 0:
					self.frontier.add(tuple([column + 1, row +  1]))
			except:
				pass
			try:
				cell = [e for e in self.grid.get_cell_list_contents(tuple([column - 1, row + 1])) if isinstance(e, Cell)][0]
				if cell.explored == 0:
					self.frontier.add(tuple([column - 1, row +  1]))
			except:
				pass

			cell = [e for e in self.grid.get_cell_list_contents(tuple([column, row])) if isinstance(e, Cell)][0]
			# Dove viene deployato il robot viene deployato anche un bean (uno solo)
			if not cell.wifi_bean:
				cell.wifi_bean = True
				for index in self.grid.get_neighborhood(cell.pos, "moore", include_center = False, radius = self.wifi_range):
					# cell = self.agent_get_cell(index)
					cell = [e for e in self.grid.get_cell_list_contents(index) if isinstance(e, Cell)][0]
					cell.wifi_covered = True
				if self.dump_datas:
					self.deployed_beans_at_start += 1		

	# what the model does at each time step
	def step(self):
		# call step function for all of the robots in random order
		self.schedule.step()
		print("step " + str(self.schedule.steps))

		if self.dump_datas:		
			# result = self.get_explored(self)
			self.dc_percentage_step.collect(self)
			self.dc_robot_status.collect(self)
		if self.optimization_task:
			self.total_idling_time += self.get_number_robots_status(self, "idling")
		if self.gamma_variation:
			distances = self.compute_robot_distances(self)
			self.gamma_df = self.gamma_df.append({"step": self.get_step(self), 
									   "mean": distances[0], "std": distances[1]},
									   ignore_index = True, sort = False)
		# if all seen cells have benn explored, stop the simulation
		# we do this so if there are unreachable cells, the cannot be seen, so the simulation stops anyway
		stop = True
		for node in self.seen_graph.nodes():
			cell = [obj for obj in self.grid.get_cell_list_contents(node) if isinstance(obj, Cell)][0]
			if cell.explored == 0 or cell.explored == 1:
				stop = False
		if stop:
			print("Simultation ended in " + str(self.schedule.step()) + " steps")
			# Data collection
			if self.dump_datas:
				df = pd.read_csv(self.time_csv)
				df = df.append({"nrobots": self.nrobots, "ncells": self.ncells, 
								"steps": self.schedule.steps, 
								"beans_deployed": self.get_number_bean_deployed(self),
								"total_difficulty": self.total_difficulty},
								ignore_index = True)
				df.to_csv(self.time_csv, index = False)
				
				df_explored = self.dc_percentage_step.get_model_vars_dataframe()
				df = pd.read_csv(self.exploration_percentage_csv)
				if len(df["sim_id"]) == 0: # in case the csv has no values
					df_explored["sim_id"] = 0
				else:
					df_explored["sim_id"] = df["sim_id"][df.index[-1]] + 1 # get the last value of sim_id increase of one
				df = df.append(df_explored, ignore_index = True, sort = False) # If there are some problems in the csvs, look for this sort, DP
				df.to_csv(self.exploration_percentage_csv, index = False)

				df_robots_status = self.dc_robot_status.get_model_vars_dataframe()
				df = pd.read_csv(self.robot_status_csv)
				if len(df["sim_id"]) == 0:
					df_robots_status["sim_id"] = 0
				else:
					df_robots_status["sim_id"] = df["sim_id"][df.index[-1]] + 1
				df = df.append(df_robots_status, ignore_index = True, sort = False)
				df.to_csv(self.robot_status_csv, index = False)

			if self.alpha_variation:
				mean = round(np.mean(self.costs_each_path), 3)
				std = round(np.std(self.costs_each_path), 3)
				df = pd.read_csv(self.alpha_csv)
				df = df.append({"nrobots": self.nrobots, "radar_radius": self.radar_radius,
							   "alpha": self.alpha, "gamma": self.gamma, "mean": mean,
							   "std": std}, ignore_index = True)
				df.to_csv(self.alpha_csv, index = False)

			if self.gamma_variation:
				df = pd.read_csv(self.gamma_csv)
				if len(df["sim_id"]) == 0:
					self.gamma_df["sim_id"] = 0
				else:
					self.gamma_df["sim_id"] = df["sim_id"][df.index[-1]] + 1
				self.gamma_df["nrobots"] = self.nrobots
				self.gamma_df["radar_radius"] = self.radar_radius
				self.gamma_df["alpha"] = self.alpha
				self.gamma_df["gamma"] = self.gamma
				df = df.append(self.gamma_df, ignore_index = True, sort = False)
				df.to_csv(self.gamma_csv, index = False)

			self.running = False

	def run_model(self):
		while(True):
			# search for unexplored cells
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

	# Data collection utilities
	@staticmethod
	def get_step(m):
		return m.schedule.steps

	# this should be the bottlenck of data collection
	@staticmethod
	def get_explored(m):
		count_explored = 0
		for i in m.grid.coord_iter():
			cell = [obj for obj in m.grid.get_cell_list_contents(i[1:]) if isinstance(obj, Cell)][0]
			if cell.explored == 2:
				count_explored += 1
		result = count_explored / (m.ncells * m.ncells - m.nobstacle)
		return result

	# these two should go faster since cells are not in the scheduler anymore
	@staticmethod
	def get_number_robots_status(m, status):
		status_value = {"idling": 0, "travelling": 1, "exploring": 2, "deploying_bean": 3}
		return len([x for x in m.schedule.agents if isinstance(x, Robot) and x.status == status_value[status]])

	@staticmethod
	def get_number_bean_deployed(m):
		return sum([x.number_bean_deployed for x in m.schedule.agents if isinstance(x, Robot)]) + m.deployed_beans_at_start

	# function for gamma variation	
	@staticmethod
	def compute_robot_distances(m):
		nrobots = m.nrobots
		T_up = np.full((nrobots, nrobots), 0.0) # if it's only zero, numpy represents only integers 
		# didn't dig deep in numpy doc but it looks like it handles triangualr matrices as "normal" matrices, so 
		# i just initilize a full matrix and then i'll use it as a triangular.
		robots = [x for x in m.schedule.agents if isinstance(x, Robot)]
		# the order of the robots in robots can change from step to step (due to the random scheduler),
		# This shouldn't create any type of problem, but to avoid a lot of problems with indexes later on
		# we sort them basing on the unique_id
		robots.sort(key = lambda x: x.unique_id)
		# I need the lowest id to shift back the ids to fit the matrices coordinations
		lowest_id = robots[0].unique_id
		for r in robots:
			matrix_id_row = r.unique_id - lowest_id
			# the distance of a robot to itself is zero by definition
			y1, x1 = r.pos
			for i in range(matrix_id_row + 1, nrobots):
				r2 = robots[i] # i can do this because they are sorted
				y2, x2 = r2.pos
				T_up[matrix_id_row][i] = distance.euclidean([x1, y1], [x2, y2])
		print(T_up)
		mean_dist_robots = list()
		mean_robot_zero = sum(T_up[0, 1 : nrobots])
		mean_dist_robots.append(mean_robot_zero)
		for i in range(1, nrobots - 1): # the last row has no values, i iters the rows
			mean_robot = (sum(T_up[0 : i, i]) + sum(T_up[i, i + 1 : nrobots])) / (nrobots - 1)
			mean_dist_robots.append(mean_robot)
		return tuple([round(np.mean(mean_dist_robots), 3), round(np.std(mean_dist_robots), 3)])
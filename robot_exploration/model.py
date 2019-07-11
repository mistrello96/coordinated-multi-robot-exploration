from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
import numpy as np
import math
import heapq
import networkx as nx

class ExplorationArea(Model):
	def __init__(self, nrobots, radar_radius, ncells, obstacles_dist, wifi_range, alpha):
		self.nrobots = nrobots
		self.radar_radius = radar_radius
		self.ncells = ncells
		self.obstacles_dist = obstacles_dist
		#self.wifi_range = wifi_range
		self.alpha = alpha

		self.grid = MultiGrid(ncells, ncells, torus=False)
		self.schedule = RandomActivation(self)

        # create grid attributes
		self.grid_traversability = dict()
		self.grid_difficulty = dict()
		self.grid_explored = dict()
		self.grid_priority = dict()
		self.grid_utility = dict()

		for i in self.grid.coord_iter():
			rand = np.random.random_sample()
			self.grid_traversability[i[1:]] = True if rand > self.obstacles_dist else False
			if self.grid_traversability[i[1:]]:
				self.grid_difficulty[i[1:]] = np.random.randint(low = 1, high=13)
				self.grid_explored[i[1:]] = False
				self.grid_priority[i[1:]] = False
				self.grid_utility[i[1:]] = 1.0
			else:
				self.grid_difficulty[i[1:]] = math.inf
				self.grid_explored[i[1:]] = None
				self.grid_priority[i[1:]] = False
				self.grid_utility[i[1:]] = -math.inf
  			
		self.seen_graph = nx.DiGraph()
		#TODO wifi representation

		# create agents
		for i in range(self.nrobots):
			# Add the agent to a random grid cell??
			#x = self.random.randrange(self.grid.width)
			#y = self.random.randrange(self.grid.height)
			x = 0
			#y = self.grid.height / 2
			y = 0
			a = Robot(i, self, tuple([x,y]),self.radar_radius)
			self.schedule.add(a)
			self.grid.place_agent(a, (x, y))
			self.grid_explored[tuple([x,y])] = True

	# what the model do at each time step
	def step(self):
		# call step function for all of the robots in random order
		self.schedule.step()
		print(list(self.grid_explored.values()).count(True) / list(self.grid_explored.values()).count(False))

	def run_model(self):
		while(True):
			if (False in self.grid_explored.values()):
				self.step()
			else:
				break
		#TODO
		# implement search untill victim found

class Robot(Agent):
	def __init__(self, unique_id, model, pos, radar_radius):
		super().__init__(unique_id, model)
		# self pos is already initializated
		self.last_pos = tuple()
		self.pos = pos
		self.radar_radius = radar_radius
		self.target_path = list()
		heapq.heapify(self.target_path)
		self.target_cell = ()
		self.exploration_treshold = math.inf
		self.exploration_status = 0
		self.percept()

	def percept(self):
		for nearby in self.model.grid.iter_neighborhood(self.pos, moore=True, include_center=False, radius=self.radar_radius):
				# s is suource node, d is destination node
				s = self.pos
				d = nearby
				# check if d is reachable
				if self.model.grid_traversability[d]:
					# compute the cost of moving in that direction
					w = 1 + (self.model.grid_difficulty[d] // 4 )
					# if the edge is not yet present, add it
					if tuple([s, d]) not in self.model.seen_graph.edges():
						self.model.seen_graph.add_edge(s, d, weight=w)
				s = nearby
				d = self.pos
				w = 1 + (self.model.grid_difficulty[d] // 4 )
				if tuple([s, d]) not in self.model.seen_graph.edges():
					self.model.seen_graph.add_edge(s, d, weight=w)
	
	def find_frontier_cells(self):
		frontier_cells = list()
		for cell in self.model.grid_explored.keys():
			if not self.model.grid_explored[cell]:
				for element in self.model.grid.get_neighborhood(cell, "moore", include_center=False, radius=1):
					if self.model.grid_explored[element]:
						frontier_cells.append(cell)
						break
		return frontier_cells

	def find_best_cell(self, frontier_cells):		
		# NB we are computing path to not explored cell that are near explored cells.
		# Since the they are close, the unexplored cell has already been seen and added to the graph
		# only consider seen cells that are not blocked for the SP computation
		# list of tuples, the first element is the cell, the second is the cost
		bids = list()
		for cell in frontier_cells:
			try:
				dist = nx.astar_path_length(self.model.seen_graph, self.pos, cell, weight='weight')
				bids.append((cell, dist))
			except:
				# if the path is not known, the cell is not considered
				pass
		# pick the most convinient cell
		best_cell = tuple()
		best_gain = -math.inf
		best_cost = 0
		for element in bids:
			cell, cost = element
			gain = self.model.grid_utility[cell] - (self.model.alpha * cost)
			if gain > best_gain:
				best_gain = gain
				best_cell = cell
				best_cost = cost
			# in case of same gain, prefer smaller distance to travel
			if gain == best_gain:
				if cost < best_cost:
					best_gain = gain
					best_cell = cell
					best_cost = cost						
		return best_cell

	def distance(self, cell1, cell2):
		x1, y1 = cell1
		x2, y2 = cell2
		dx = abs(x2 - x1);
		dy = abs(y2 - y1);

		minimum = min(dx, dy);
		maximum = max(dx, dy);

		diagonalSteps = minimum;
		straightSteps = maximum - minimum;

		#return math.sqrt(2) * diagonalSteps + straightSteps;
		return diagonalSteps + straightSteps


	def step(self):
		# if the agent has a move to get closer to the target, move towards it
		if list(self.target_path):
			# update the last position
			self.last_pos = self.pos
			# move the agent
			self.model.grid.move_agent(self, heapq.heappop(self.target_path))
			# find the cell that the robot can see
			self.percept()
			# TODO wifi range check
		else:
			# if the agent has no move to do, but is on the target, explore
			if self.target_cell:
				if self.exploration_status < self.exploration_treshold:
					self.exploration_status += 1
				# if the agent has ended the exploration, update the data
				else:
					self.exploration_treshold = math.inf
					self.exploration_status = 0
					self.model.grid_explored[self.target_cell] = True
					self.target_cell = ()
			# if the robot has no target, find one
			else:
				frontier_cells = self.find_frontier_cells()
				self.target_cell = self.find_best_cell(frontier_cells)
				# if no frontier is avaiable, just pass
				if (self.target_cell):
					self.exploration_treshold = self.model.grid_difficulty[self.target_cell]
					# not sure if make sense
					self.model.grid_utility[self.target_cell] = -math.inf
					# compute and store the most convinient path to get there
					self.target_path = nx.astar_path(self.model.seen_graph, self.pos, self.target_cell, weight='weight')
					# reduce the utility of the FRONTIERS (and only frontiers) cells nearby the target cell
					for element in self.model.grid.get_neighborhood(self.target_cell, "moore", include_center=False, radius=self.radar_radius):
						if element in frontier_cells:
							#self.model.grid_utility[elemet] -= (1 - self.distance(self.target_cell, element) / self.radar_radius)
							self.model.grid_utility[element] *= (1 - self.distance(self.target_cell, element) / self.radar_radius)
		print(self.pos)
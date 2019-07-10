from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
import numpy as np
import math
import heapq
import networkx as nx

class ExplorationArea(Model):
	def __init__(self):
		self.nrobots = nrobots
		self.radar_radius = radar_radius
		self.ncells = ncells
		self.obstacles_dist = obstacles_dist
		self.wifi_range = wifi_range
		self.alpha = alpha
		self.gamma = gamma

		self.grid = MultiGrid(ncells, ncells, torus=False)
        self.schedule = RandomActivation(self)

        # create grid attributes
        self.grid_traversability = dict()
        self.grid_difficulty = dict()
        self.grid_explored = dict()
        #self.grid_seen = dict()
        self.grid_priority = dict()

        for i in self.grid.coord_iter():
        	rand = np.random.random_sample()
        	grid_traversability[i[1:]] = 1 if rand > self.obstacles_dist else grid_traversability[i[1:]] = 0
  			grid_difficulty[i[1:]] = numpy.random.randint(low = 1, high=13)
  			grid_explored[i[1:]] = False
  			#grid_seen[i[1:]] = False
  			grid_priority[i[1:]] = False
  			grid_utility[i[1:]] = 1.0
  			seen_graph = nx.DiGraph()
  			seen_graph.add_node((0,0))
  			#TODO wifi representation

        # create agents
        for i in range(self.nrobots):
			a = Robot(i, self. radar_radius)
			self.schedule.add(a)
			# Add the agent to a random grid cell
			#x = self.random.randrange(self.grid.width)
			#y = self.random.randrange(self.grid.height)
			x = 0
			#y = self.grid.height / 2
			y = 0
			self.grid.place_agent(a, (x, y))

	# what the model do at each time step
	def step(self):
		# call step function for all of the robots in random order
		self.schedule.step()

    def run_model(self, n):
        while(False in grid_explored.itervalues())
            self.step()
        #TODO
        # implement search untill victim found

class Robot(Agent):
	def __init__(self, unique_id, model, radar_radius):
		super().__init__(unique_id, model)
		# self pos is already initializated
		self.last_pos = self.pos
		self.radar_radius = radar_radius
		self.target_path = list()
		heapq.heapify(self.target_path)
		self.target_cell = ()
		self.exploration_treshold = math.inf
		self.exploration_status = 0

	def percept(self):
		for nearby in self.model.grid.iter_neighborhood(self.pos, moore=True, include_center=False, radius=self.radar_radius):
				# TOREMOVE
				#self.model.grid_seen[nearby] = True
				# s is suource node, d is destination node
				s = self.pos
				d = nearby
				# check if d is reachable
				if self.model.grid_traversability[d]:
					# compute the cost of moving in that direction
					w = 1 + (self.model.grid_difficulty[d] // 4 )
					# if the edge is not yet presdent, add it
					if tuple([s, d]) not in self.model.seen_graph.edges():
						self.model.seen_graph.add_weighted_edges_from(tuple([s, d, w]))
				s = nearby
				d = self.pos
				w = 1 + (self.model.grid_difficulty[d] // 4 )
				if tuple([s, d]) not in self.model.seen_graph.edges():
					self.model.seen_graph.add_weighted_edges_from(tuple([s, d, w]))
	
	def find_best_cell(self):
		# find the frontier cells
		frontier_cells = list()
		for cell in grid_explored.keys():
			if not grid_explored[cell]:
				for element in self.model.get_neighborhood(cell, moore, include_center=False, radius=1):
					if grid_explored[element]:
						frontier_cells.append(cell)
						break
		# NB we are computing path to not explored cell that are near explored cells.
		# Since the they are close, the unexplored cell has already been seen and added to the graph
		# only consider seen cells that are not blocked for the SP computation
		# list of tuples, the first element is the cell, the second is the cost
		bids = list()
		for cell in frontier_cells:
			try:
				dist = nx.astar_path_length(seen_graph, self.pos, cell, weight='weight')
				bids.append((cell, dist))
			except:
				# if the path is not known, the cell is not considered
				pass
		# pick the most convinient cell
		best_cell = tuple()
		best_gain = -math.inf
			for element in bids:
				cell, cost = element
				gain = self.model.alpha * self.model.grid_utility[cell] - self.model.gamma * cost
				if gain > best_gain:
					best_gain = gain
					best_cell = cell
		return best_cell




	def step(self):
		# if the agent has a move to get closer to the target, move towards it
		if not list(self.target_path):
			# update the last position
			self.last_pos = self.pos
			# move the agent
			self.model.grid.move_agent(self, heapq.heappop(target_path))
			# find the cell that the robot can see
			self.percept()
			# TODO wifi range check
		else:
			# if the agent has no move to do, but is on the target, explore
			if not target_cell:
				if exploration_status < exploration_treshold:
					exploration_status ++
				# if the agent has ended the exploration, update the data
				else:
					self.exploration_treshold = math.inf
					self.exploration_status = 0
					self.model.grid_explored[self.target_cell] = True
					self.target_cell = ()
			# if the robot has no target, find one
			else:
 				self.target_cell = self.find_best_cell()
 				# NB, in the real life, the 
 				self.exploration_treshold = self.model.grid_difficulty[best_cell]
				# compute and store the most convinient path
				self.target_path = nx.astar_path(self.model.seen_graph, self.pos, cell, weight='weight')
				# reduce the utility of the cells nearby the target cell
				for element in self.model.get_neighborhood(self.target_cell, moore, include_center=False, radius=self.radar_radius):
				



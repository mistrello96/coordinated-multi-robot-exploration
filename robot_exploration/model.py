from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
import numpy as np
import math
import heapq

class ExplorationArea(Model):
	def __init__(self):
		self.nrobots = nrobots
		self.seen_radius = seen_radius
		self.ncells = ncells
		self.obstacles_dist = obstacles_dist
		self.wifi_range = wifi_range

		self.grid = MultiGrid(ncells, ncells, torus=False)
        self.schedule = RandomActivation(self)

        # create grid attributes
        self.grid_traversability = dict()
        self.grid_difficulty = dict()
        self.grid_explored = dict()
        self.grid_seen = dict()
        self.grid_priority = dict()

        for i in self.grid.coord_iter():
        	rand = np.random.random_sample()
        	grid_traversability[i[1:]] = 1 if rand > self.obstacles_dist else grid_traversability[i[1:]] = 0
  			grid_difficulty[i[1:]] = numpy.random.randint(low = 1, high=13)
  			grid_explored[i[1:]] = False
  			grid_seen[i[1:]] = False
  			grid_priority[i[1:]] = False
  			grid_utility[i[1:]] = 1.0
  			#TODO wifi representation

        # create agents
        for i in range(self.nrobots):
			a = Robot(i, self. seen_radius)
			self.schedule.add(a)
			# Add the agent to a random grid cell
			#x = self.random.randrange(self.grid.width)
			#y = self.random.randrange(self.grid.height)
			x = 0
			y = self.grid.height / 2
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
	def __init__(self, unique_id, model, seen_radius):
		super().__init__(unique_id, model)
		# self pos is already initializated
		self.last_pos = self.pos
		self.seen_radius = seen_radius
		self.target_heap = list()
		heapq.heapify(self.target_heap)
		self.target_cell = ()
		self.exploration_treshold = math.inf
		self.exploration_status = 0


	def step(self):
		# if the agent has a move to get closer to the target, move towards it
		if not list(self.target):
			self.last_pos = self.pos
			self.model.grid.move_agent(self, heapq.heappop(target))
			for n in self.model.grid.iter_neighborhood(self.pos, moore=True, include_center=False, radius=self.seen_radius):
				self.model.grid_seen[n] = True
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
				frontier_cells
				



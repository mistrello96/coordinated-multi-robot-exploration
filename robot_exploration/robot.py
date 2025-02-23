from .cell import Cell
from mesa import Agent
import math
import networkx as nx
from decimal import Decimal, ROUND_HALF_UP
import time
import random as rnd

class Robot(Agent):
	def __init__(self, unique_id, model, pos, radar_radius):
		super().__init__(unique_id, model)
		self.last_pos = tuple()
		self.pos = pos
		# seen radius of the robot
		self.radar_radius = radar_radius
		# queue with the path to the target
		self.target_path = list()
		# a tuple with the indexes of the target
		self.target_cell = ()
		# store the number of steps needed to explore the cell
		self.exploration_treshold = math.inf
		# progress of the exploration process
		self.exploration_status = 0
		# store the number of steps needed to explore the cell
		cell = self.agent_get_cell(self.pos)
		self.travel_treshold = 1 + (cell.difficulty // 4)
		# progress of the crossing process
		self.travel_status = 0
		# used for failure cases in order to set back correctly the utility of the cell
		self.former_cell_utility = 0

		self.percept()

		# store the status of the Robot
		# 0 picking target / not moving
		# 1 travelling
		# 2 exploring
		# 3 deploying wifi bean
		# -1 failed
		self.status = 0
		# if covered by a wifi bean
		self.out_of_range = False # all'inizio la persona o il mezzo che li deploya porta con sè un bean
		# store the number of steps needed for a wifi bean deploy
		self.deploy_threshold = 15
		# progress of the deploy process
		self.deploy_status = 0
		# used for data collection
		self.number_bean_deployed = 0
		rnd.seed()

	# return the cell agent at the index given
	def agent_get_cell(self, index):
		tmp = self.model.grid.get_cell_list_contents(index)
		cell = [obj for obj in tmp if isinstance(obj, Cell)][0]
		return cell

	# return the injured agent at the index given
	def agent_get_injured(self, index):
		tmp = self.model.grid.get_cell_list_contents(index)
		try:
			return [obj for obj in tmp if isinstance(obj, Injured)][0]
		except:
			return None

	def failure(self):
		failure = rnd.random() > (1 - 10e-8)
		if failure:
			if self.target_cell:
				cell = self.agent_get_cell(self.target_cell)
				cell.explored = 0
				cell.utility = self.former_cell_utility
				self.model.frontier.add(self.target_cell)
			self.model.schedule.remove(self)
			self.status = -1
		return failure

	# return cells of the supercover line between 2 cells
	def line_of_sight(self, source, destination):
		y0, x0 = source
		y1, x1 = destination
		path = list()
		dx = abs(x1 - x0)
		dy = abs(y1 - y0)
		x = x0
		y = y0
		n = 1 + dx + dy
		x_inc = 1 if x1 > x0 else -1
		y_inc =1 if y1 > y0 else -1
		error = dx - dy
		dx *= 2
		dy *= 2
		while n > 0:
			path.append(tuple([y,x]))
			if error > 0:
				x += x_inc
				error -= dy
			else: 
				y += y_inc
				error += dx
			n -= 1
		valid = True
		for cell_index in path:
			cell = self.agent_get_cell(cell_index)
			if cell.explored == -1:
				valid = False
		return valid

	# add the sorrundings of the cell to the graph used for SP computation
	def percept(self):
		# iterate over the neighborhood
		robot_seen = set(self.model.grid.get_neighborhood(self.pos, "moore", include_center = True, radius = self.radar_radius))
		for percepted_cell in robot_seen:
			cell_neigh = set(self.model.grid.get_neighborhood(percepted_cell, "moore", include_center = False, radius = 1))
			cell_neigh_percepted = set.intersection(robot_seen, cell_neigh)
			for neigh_cell in cell_neigh_percepted:
				source_index = percepted_cell
				destination_index = neigh_cell
				source_cell = self.agent_get_cell(source_index)
				destination_cell = self.agent_get_cell(destination_index)
				# check if cells are not obstacles
				if self.line_of_sight(self.pos, source_index) and self.line_of_sight(self.pos, destination_index) and self.line_of_sight(source_index, destination_index):
					# compute the cost of moving in that direction
					# the cost is the thick number required to go across the cell
					w = int(Decimal(0.5 * source_cell.difficulty).to_integral_value(rounding = ROUND_HALF_UP))
					# if the edge is not yet present in the graph, add it
					if tuple([source_index, destination_index]) not in self.model.seen_graph.edges():
						self.model.seen_graph.add_edge(source_index, destination_index, weight = w)
				# add the reversed edge if not present
				source_index = neigh_cell
				destination_index = percepted_cell
				source_cell = self.agent_get_cell(source_index)
				destination_cell = self.agent_get_cell(destination_index)
				if self.line_of_sight(self.pos, source_index) and self.line_of_sight(self.pos, destination_index) and self.line_of_sight(source_index, destination_index):
					w = int(Decimal(0.5 * source_cell.difficulty).to_integral_value(rounding = ROUND_HALF_UP))
					if tuple([source_index, destination_index]) not in self.model.seen_graph.edges():
						self.model.seen_graph.add_edge(source_index, destination_index, weight = w)


	# find the most convinient cell to explore for a robot
	def find_best_cell(self):
		# NB we are computing path to not explored cells that are near explored cells.
		# Since they are close, the unexplored cell has already been seen at least one time and added to the graph
		# only consider seen cells that are not obstacles for the SP computation
		
		# if there are no cells in the frontier, there can't be a valid target
		if self.model.frontier == set(): # ci sarà sicuramente una funzione is empty
			return tuple()
		# list of tuples, the first element is the indexes of the cell, the second is the cost to get there
		bids = list()
		try:
			dist = nx.shortest_path_length(self.model.seen_graph, source = self.pos, weight = 'weight', method = 'dijkstra')
		except:
			# if the path is not found, the cell is not considered
			pass
		for i in list(self.model.frontier):
			try:
				bids.append((i, dist[i]))
			except:
				pass
		# pick the most convinient cell
		bids_sort_cost = sorted(bids, key = lambda x: x[1])
		bids_sort_gain = sorted(bids_sort_cost, key = lambda x: (self.agent_get_cell(x[0]).priority + self.agent_get_cell(x[0]).utility - (self.model.alpha * x[1])), reverse = True)
		
		# if bids_sort_gain is not None and every cell has -inf utility, no valid target is found
		if not bids_sort_gain:
			return tuple()
		if self.agent_get_cell(bids_sort_gain[0][0]).utility == -math.inf:
			# in order to avoid two robots exploring the same cell
			return tuple()
		else:
			# if find cells, pick the most convinient one
			result = bids_sort_gain[0][0]
			
			if self.model.alpha_variation:
				path_cost = bids_sort_gain[0][1]
				sim_step = self.model.get_step(self.model)
				self.model.costs_each_path.append(path_cost)
				self.model.alpha_step[sim_step].append(path_cost)

			self.model.frontier.remove(result)
			# reduce the utility of all the sorrundings cell if not visited yet
			for element in self.model.grid.get_neighborhood(result, "moore", include_center = False, radius = self.radar_radius):
				# only if the cell is in lof with the robot
				#if self.line_of_sight(self.pos, element):
				cell2 = self.agent_get_cell(element)
				if cell2.explored == 0:
					cell2.prev_utility = cell2.utility
					cell2.utility *= self.model.gamma * (self.distance(result, element) / self.radar_radius)

			return result

	# return distance between 2 cells (ignore diagonal distortion)
	def distance(self, cell1, cell2):
		y1, x1 = cell1
		y2, x2 = cell2
		dx = abs(x2 - x1);
		dy = abs(y2 - y1);

		minimum = min(dx, dy);
		maximum = max(dx, dy);

		diagonalSteps = minimum;
		straightSteps = maximum - minimum;

		#return math.sqrt(2) * diagonalSteps + straightSteps;
		return diagonalSteps + straightSteps

	def wifi_deploy(self):
		# if it is the first step of the deploy, update status of robot and move back into the cell
		if not self.deploy_status:
			self.status = 3
			# put the current position into the path
			self.target_path.insert(0, self.pos) 
			# move back
			self.model.grid.move_agent(self, self.last_pos)
			self.last_pos = None
			# start deploy
			self.deploy_status += 1
		# go on with the relase process
		else:
			self.deploy_status += 1
		# if the release is completed, update the grid data with the new bean
		if self.deploy_status == self.deploy_threshold:
			failure = rnd.random() > (1 - 10e-8)
			if not failure:
				cell = self.agent_get_cell(self.pos)
				cell.wifi_bean = True
				# update wifi signal
				for index in self.model.grid.get_neighborhood(self.pos, "moore", include_center = False, radius = self.model.wifi_range):
					cell = self.agent_get_cell(index)
					cell.wifi_covered = True
				# reset deploy variables
				self.out_of_range = False
				self.deploy_status = 0
				self.number_bean_deployed += 1
			else:
				self.out_of_range = False
				self.deploy_status = 0
				self.number_bean_deployed += 1
				self.model.broken_beans += 1

	def move(self):
		self.status = 1
		# if a cell has been complitelly crossed, go to the next one
		if self.travel_status == self.travel_treshold:
			# update the last position
			self.last_pos = self.pos
			# move the agent
			self.model.grid.move_agent(self, self.target_path[0])
			self.target_path = self.target_path[1:]
			# find the cell that the robot can see and add to the graph
			self.percept()
			cell = self.agent_get_cell(self.pos)
			# update crossing status and treshold
			self.travel_status = 0
			self.travel_treshold = Decimal(0.5 * cell.difficulty).to_integral_value(rounding = ROUND_HALF_UP)
			# check if signal has been lost
			if not cell.wifi_covered:
				self.out_of_range = True
				self.deploy_status = 0
		# otherwise, go on with the crossing process
		else:
			self.travel_status += 1	

	def explore(self):
		# update robot status
		self.status = 2
		if self.exploration_status == 0:
			# correct utility if cell not seen
			for element in self.model.grid.get_neighborhood(self.pos, "moore", include_center = False, radius = self.radar_radius):
				# only if the cell is in lof with the robot
				if not self.line_of_sight(self.pos, element):
					cell2 = self.agent_get_cell(element)
					if cell2.explored == 0:
						cell2.utility = cell2.prev_utility
			# expand frontier
			for element in self.model.grid.get_neighborhood(self.pos, "moore", include_center = False, radius = 1):
				# only if the cell is in lof with the robot
				if self.line_of_sight(self.pos, element):
					cell2 = self.agent_get_cell(element)
					if cell2.explored == 0:
						self.model.frontier.add(cell2.pos)
		# if the cell is not yet full explored, keep going
		if self.exploration_status < self.exploration_treshold:
			# if first step of exploration, update cell status
			if self.exploration_status == 0:
				cell = self.agent_get_cell(self.pos)
				cell.explored = 1
			# anyway, explore
			self.exploration_status += 1
		# if the agent has finished the exploration, update the data of the cell (and self data)
		else:
			self.exploration_treshold = math.inf
			self.exploration_status = 0
			self.target_cell = ()
			cell = self.agent_get_cell(self.pos)
			cell.explored = 2
			injured = self.agent_get_injured(self.pos)
			if injured:
				injured.status = 1

		
	def pick_target(self):
		# update robot status
		self.status = 0
		# find best cell
		self.target_cell = self.find_best_cell()
		# if no frontier is avaiable, just stand still
		# else, update the self data
		if self.target_cell:
			cell = self.agent_get_cell(self.target_cell)
			# speed is reduced by half when exploring. The cell is divided in 6 lanes
			self.exploration_treshold = 6 * int(Decimal(0.5 * cell.difficulty).to_integral_value(rounding = ROUND_HALF_UP)) * 2
			# make the cell disgusting for other robots
			self.former_cell_utility = cell.utility
			cell.utility = -math.inf
			# compute and store the most convinient path to get there
			self.target_path = nx.shortest_path(self.model.seen_graph, source = self.pos, target = self.target_cell, weight = 'weight', method = 'dijkstra')
			# the first element is the cell itself, so pop it
			self.target_path = self.target_path[1:]

	def step(self):
		f = self.failure()
		if f:
			return
		# if the robot has lost wifi signal
		if self.out_of_range:
			self.wifi_deploy()
		# if the robot is in signal and
		# if the agent has a move to get closer to the target, move towards it
		else:
			if self.target_path:
				self.move()		
			else:
				# if the agent has no move to do, but has a target, it must be on the target cell, so explore
				if self.target_cell:
					self.explore()
				# if the robot has no target, find one
				else:
					self.pick_target()
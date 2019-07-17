from .cell import Cell
from mesa import Agent
import math
import networkx as nx

# TODO
# prioritize cells with victims

# Minors
# rewrite find_frontier_cells

class Robot(Agent):
	def __init__(self, unique_id, model, pos, radar_radius):
		super().__init__(unique_id, model)
		self.last_pos = tuple()
		self.pos = pos
		self.radar_radius = radar_radius
		# queue with the path to the target
		self.target_path = list()
		# a tuple with the indexes of the target
		self.target_cell = ()
		# store the number of steps needed to explore the cell
		self.exploration_treshold = math.inf
		self.exploration_status = 0
		self.can_move = False
		cell = self.agent_get_cell(self.pos)
		# store the number of steps needed to explore the cell
		self.travel_status = 0
		self.travel_treshold = 1 + (cell.difficulty // 4)
		self.percept()
		# store the status of the Robot
		# 0 picking target / not moving
		# 1 travelling
		# 2 exploring
		self.status = 0
		# add self.status for robot task (moving/exploring/waiting)

	# return the cell agent at the index given
	def agent_get_cell(self, index):
		tmp = self.model.grid.get_cell_list_contents(index)
		cell = [obj for obj in tmp if isinstance(obj, Cell)][0]
		return cell

	def line_of_sight(self, source, destination):
		x0, y0 = source
		x1, y1 = destination
		#y0 = self.model.ncells - y0
		#y1 = self.model.ncells - y1
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
			path.append(tuple([x,y]))
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
			cell_neigh_percepted = set.intersection(robot_seen, cell_neigh) # DP inter isn't definetely a clear variable name
			for neigh_cell in cell_neigh_percepted:
				source_index = percepted_cell
				destination_index = neigh_cell
				source_cell = self.agent_get_cell(source_index)
				destination_cell = self.agent_get_cell(destination_index)
				# check if cells are not obstacles
				if self.line_of_sight(self.pos, source_index) and self.line_of_sight(self.pos, destination_index) and self.line_of_sight(source_index, destination_index):
					# compute the cost of moving in that direction
					w = 1 + (source_cell.difficulty // 4)
					# if the edge is not yet present in the graph, add it
					if tuple([source_index, destination_index]) not in self.model.seen_graph.edges():
						self.model.seen_graph.add_edge(source_index, destination_index, weight=w)
				# add the reversed edge if not present
				source_index = neigh_cell
				destination_index = percepted_cell
				source_cell = self.agent_get_cell(source_index)
				destination_cell = self.agent_get_cell(destination_index)
				if self.line_of_sight(self.pos, source_index) and self.line_of_sight(self.pos, destination_index) and self.line_of_sight(source_index, destination_index):
					w = 1 + (source_cell.difficulty // 4)
					if tuple([source_index, destination_index]) not in self.model.seen_graph.edges():
						self.model.seen_graph.add_edge(source_index, destination_index, weight = w)
	
	# return a list of tuples that represents the indexes of all the frontier cells
	def find_frontier_cells(self):
		frontier_cells = list()
		# iterate over all cells of the grid
		for i in self.model.grid.coord_iter():
			# pick the unexplored cell
			coord = i[1:]
			cell = self.agent_get_cell(coord)
			if cell.explored == 0:
				# iterate over the 1-radius neighborhood searching for an xplored cell
				for neighbor_coord in self.model.grid.get_neighborhood(coord, "moore", include_center = False, radius = 1):
					neighbor_cell = self.agent_get_cell(neighbor_coord)
					# maybe is more correct leave only ==2
					if neighbor_cell.explored == 1 or neigh_cell.explored == 2:
						# if found, the unexplored cell is a frontier cell
						frontier_cells.append(coord)
						break
		return frontier_cells

	# find the most convinient cell to explore for a robot
	def find_best_cell(self, frontier_cells):		
		# NB we are computing path to not explored cells that are near explored cells.
		# Since the they are close, the unexplored cell has already been seen at least one time and added to the graph
		# only consider seen cells that are not obstacles for the SP computation
		# list of tuples, the first element is the indexes of the cell, the second is the cost to get there
		bids = list()
		for i in frontier_cells:
			# try to compute the shortest path to get to the cell. If the operation succedes, add the tuple to the bids list
			try:
				dist = nx.astar_path_length(self.model.seen_graph, self.pos, i, weight = 'weight')
				bids.append((i, dist))
			except:
				# if the path is not found, the cell is not considered
				pass
		# pick the most convinient cell
		# DP, the only sort with a more complicated lambda as suggested by stackoveflow wan't enough?
		# Asking to learn.
		bids_sort_cost = sorted(bids, key = lambda x: x[1])
		bids_sort_gain = sorted(bids_sort_cost, key = lambda x: (self.agent_get_cell(x[0]).utility - (self.model.alpha * x[1])), reverse = True)
		if bids_sort_gain:				
			return bids_sort_gain[0][0]
		else:
			return tuple()

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
		if self.target_path:
			self.status = 1
			# if a cell has been traversed, go to the next one
			if self.travel_status == self.travel_treshold:
				# update the last position
				self.last_pos = self.pos
				# move the agent
				self.model.grid.move_agent(self, self.target_path[0])
				self.target_path = self.target_path[1:]
				# find the cell that the robot can see and add to the graph
				self.percept()
				cell = self.agent_get_cell(self.pos)
				self.travel_status = 0
				self.travel_treshold = 1 + (cell.difficulty // 4)
			else:
				self.travel_status += 1
			# TODO wifi range check
		
		else:
			# if the agent has no move to do, but is on the target, explore
			if self.target_cell:
				self.status = 2
				# if the cell is not yet full explored, keep going
				if self.exploration_status < self.exploration_treshold:
					# if fist step of exploration, update cell status
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

			# if the robot has no target, find one
			else:
				self.status = 0
				# find frontier's cells
				frontier_cells = self.find_frontier_cells()
				# find best cell
				self.target_cell = self.find_best_cell(frontier_cells)
				# if no frontier is avaiable, just stand still

				# DP can waiting for frontiers bring to patological situation? 
				# else, search for the sp and reduce utility near the target cell
				
				if (self.target_cell):
					cell = self.agent_get_cell(self.target_cell)
					self.exploration_treshold = cell.difficulty
					# make the cell disgusting for other robots
					cell.utility = -math.inf
					# compute and store the most convinient path to get there
					self.target_path = nx.astar_path(self.model.seen_graph, self.pos, self.target_cell, weight = 'weight')
					# the first element is the cell itself, so pop it
					self.target_path = self.target_path[1:]
					# reduce the utility of all the sorrundings cell if not visited yet
					for element in self.model.grid.get_neighborhood(self.target_cell, "moore", include_center = False, radius = self.radar_radius):
						cell2 = self.agent_get_cell(element)
						if cell2.explored == 0:
							#cell.utility -= (1 - self.distance(self.target_cell, element) / self.radar_radius)
							cell2.utility *= (1 - self.distance(self.target_cell, element) / self.radar_radius)
					## WARNING
					# this approach, proposed in the paper, leads to a pathological situation where a robot after the exploration has a cell in front
					# of him with utility 1 and cost to get there 1, so it will always pich that cell
					'''
					# reduce the utility of the FRONTIERS (and only frontiers) cells nearby the target cell
					for element in self.model.grid.get_neighborhood(self.target_cell, "moore", include_center=False, radius=self.radar_radius):
						if element in frontier_cells:
							cell2 = self.agent_get_cell(element)
							#cell.utility -= (1 - self.distance(self.target_cell, element) / self.radar_radius)
							cell2.utility *= (1 - self.distance(self.target_cell, element) / self.radar_radius)
					'''
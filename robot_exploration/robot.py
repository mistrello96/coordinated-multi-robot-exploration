from .cell import Cell
from mesa import Agent
import math
import networkx as nx


class Robot(Agent):
	def __init__(self, unique_id, model, pos, radar_radius):
		super().__init__(unique_id, model)
		# self pos is already initializated
		self.last_pos = tuple()
		self.pos = pos
		self.radar_radius = radar_radius
		# heap with the path to the target
		self.target_path = list()
		# a tuple with the indexes of the target
		self.target_cell = ()
		# store the number of steps needed to explore the cell
		self.exploration_treshold = math.inf
		self.exploration_status = 0
		self.percept()
		# add self.status for robot task (moving/exploring/waiting)

	# return the cell agent at the index given
	def agent_get_cell(self, index):
		tmp = self.model.grid.get_cell_list_contents(index)
		cell = [obj for obj in tmp if isinstance(obj, Cell)][0] # DP why only the first element?
		return cell

	# add the sorrundings of the cell to the graph used for SP computation
	def percept(self):
		# iterate over the neighborhood
		robot_seen = set(self.model.grid.get_neighborhood(self.pos, "moore", include_center = True, radius = self.radar_radius))
		# DP with include center a robot can see itself?
		for element in robot_seen:
			cell_neigh = set(self.model.grid.get_neighborhood(element, "moore", include_center = False, radius = 1))
			inter = set.intersection(robot_seen, cell_neigh) # DP inter isn't definetely a clear variable name
			for element2 in inter:
				# s is source node, d is destination node
				s = element
				d = element2
				# check if d is reachable
				# DP I think that cell_source and cell_destination can fit better
				# maybe even element and element2 can be missleading
				cell1 = self.agent_get_cell(s)
				cell2 = self.agent_get_cell(d)
				if cell1.traversability and cell2.traversability:
					# compute the cost of moving in that direction
					w = 1 + (cell1.difficulty // 4)
					# if the edge is not yet present in the graph, add it
					if tuple([s, d]) not in self.model.seen_graph.edges():
						self.model.seen_graph.add_edge(s, d, weight=w)
				# add the reversed edge if not present
				s = element2
				d = element
				cell1 = self.agent_get_cell(d)
				cell2 = self.agent_get_cell(s)
				if cell1.traversability and cell2.traversability:
					# DP I assume that traversability is a boolean
					w = 1 + (cell1.difficulty // 4) # DP I don't get it
					# DP I know that python is cool but wouldn't initilizing
					# seen_graph in the __init__ better? In order to be more clearer 
					# to the reader? 
					if tuple([s, d]) not in self.model.seen_graph.edges():
						self.model.seen_graph.add_edge(s, d, weight = w)
	
	# return a list of tuples that represents the indexes of all the frontier cells
	def find_frontier_cells(self):
		frontier_cells = list()
		# iterate over all cells of the grid
		# DP I think that we can rewrite it in a more fashonable way
		for i in self.model.grid.coord_iter():
			# pick the unexplored cell
			cell = self.agent_get_cell(i[1:])
			if cell.explored == 0:
				# iterate over the 1-radius neighborhood
				for element in self.model.grid.get_neighborhood(i[1:], "moore", include_center = False, radius = 1):
					# search for a explored cell
					cell2 = self.agent_get_cell(element)
					# maybe is more correct leave only ==2
					if cell2.explored == 1 or cell2.explored == 2:
						# if found, the unexplored cell is a frontier cell
						frontier_cells.append(i[1:])
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
		best_cell_index = tuple()
		best_gain = -math.inf
		best_cost = 0
		# iterate over the possible destination
		# DP I guess you're looking for the maximum, can't we simply sort the list 
		# using key argument?
		# somthing like this should mae the trick: sorted_by_length = sorted(list_, key=lambda x: (x[0], len(x[1]), float(x[1])))
		for element in bids:
			cell_index, cost = element
			cell = self.agent_get_cell(cell_index)
			gain = cell.utility - (self.model.alpha * cost)
			if gain > best_gain:
				best_gain = gain
				best_cell_index = cell_index
				best_cost = cost
			# in case of same gain, prefer smaller distance to travel
			if gain == best_gain:
				if cost < best_cost:
					best_gain = gain
					best_cell_index = cell_index
					best_cost = cost						
		return best_cell_index

	def distance(self, cell1, cell2):
		# DP why are calculating the distance in cells? 
		# Wouldn't our distace be the sum of the weigths to get through cells?
		# Am I missing something?
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

		# DP what values can assume target_path and target_cell? Are object with None values or empty tuples?

		if self.target_path:
			
			## TODO
			# consider path difficulty
			
			# update the last position
			self.last_pos = self.pos
			# move the agent
			self.model.grid.move_agent(self, self.target_path[0])
			self.target_path = self.target_path[1:]
			# find the cell that the robot can see and add to the graph
			self.percept()

			# TODO wifi range check
		
		else:
			# if the agent has no move to do, but is on the target, explore
			if self.target_cell:
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
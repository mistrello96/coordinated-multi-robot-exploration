from mesa.batchrunner import BatchRunner
from robot_exploration.model import ExplorationArea
import random as rnd

for alpha in [0, 0.01, 0.1, 1, 10]:
	maps_index = rnd.randint(1, 5)

	fixed_params = {
		"nrobots": 6,
		"radar_radius": 6,  
		"wifi_range": 10, 
		"alpha": alpha,
		"gamma" : 0.65,
		"dump_datas": False,
		"optimization_task": False,
		"load_file" : "./robot_exploration/maps/30_maps/random{}.py".format(maps_index),
		"alpha_variation" : True # record datas for alpha variation studies
	}

	batch_run = BatchRunner(
		ExplorationArea,
		None,
		fixed_params,
		iterations = 10,
		max_steps = 10000
	)

	batch_run.run_all()

for gamma in [0, 0.01, 0.1, 0.5, 1]:
	maps_index = rnd.randint(1, 5)

	fixed_params = {
		"nrobots": 6,
		"radar_radius": 6,  
		"wifi_range": 10, 
		"alpha": 8.175,
		"gamma" : gamma,
		"dump_datas": False,
		"optimization_task": False,
		"load_file" : "./robot_exploration/maps/30_maps/random{}.py".format(maps_index),
		"gamma_variation" : True, # record datas for alpha variation studies
		"gamma_csv" : "./robot_exploration/results/gamma_variation{}.csv".format(gamma)
	}

	batch_run = BatchRunner(
		ExplorationArea,
		None,
		fixed_params,
		iterations = 10,
		max_steps = 10000
	)

	batch_run.run_all()



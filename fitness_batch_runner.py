from mesa.batchrunner import BatchRunner
from robot_exploration.model import ExplorationArea
import random as rnd
import pandas as pd

def fitness(nrobots, maps_index):
	fixed_params = {
		"nrobots": nrobots,
		"radar_radius": 6, 
		"wifi_range": 3, 
		"alpha": 8.175,
		"gamma" : 0.65,
		"dump_datas": True,
		"optimization_task": True,
		"load_file" : "./robot_exploration/maps/30_maps/random{}.py".format(maps_index)
	}

	batch_run = BatchRunner(
		ExplorationArea,
		None,
		fixed_params,
		iterations = 1,
		max_steps = 10000,
		model_reporters = {"step": lambda m: m.schedule.steps,
						   "total_idling": lambda m: m.total_idling_time}
	)

	batch_run.run_all()
	run_data = batch_run.get_model_vars_dataframe()
	return run_data["step"].iloc[0] + (run_data["total_idling"].iloc[0] / nrobots)


for nrobots in range(51, 80, 5):
	for i in range(0, 10):
		maps_index = rnd.randint(1, 5)
		fit = fitness(nrobots, maps_index)
		df = pd.read_csv("./robot_exploration/results/fitness_analysis.csv")
		df = df.append({
		"sim_index" : i,
		"nrobots" : nrobots,
		"fitness" : fit,
		"radar_radius": 6, 
		"wifi_range": 3, 
		"alpha": 8.175,
		"gamma" : 0.65}, ignore_index = True)
		print(df)
		df.to_csv("./robot_exploration/results/fitness_analysis.csv", index = False)
from mesa.batchrunner import BatchRunner
from robot_exploration.model import ExplorationArea

def fitness(nrobots, radar_radius, alpha):
	fixed_params = {
		"nrobots": nrobots,
		"radar_radius": radar_radius, 
		"ncells": 5, 
		"obstacles_dist": 0.01, 
		"wifi_range": 10, 
		"alpha": alpha,
		"ninjured": 4,
		"dump_datas": False,
		"optimization_task": True
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
	#print("tempo da sum" + str(sum(run_data["step"])))
	#print(sum(run_data["total_idling"]))
	return run_data["step"] + (run_data["total_idling"] / nrobots)
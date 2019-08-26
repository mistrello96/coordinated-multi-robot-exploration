from mesa.batchrunner import BatchRunner
from robot_exploration.model import ExplorationArea

def fitness(list_params):
	'''
	list_params[0] is the number of the robots which has to be an integer
	list_params[1] is the radar radius which has to be an integer
	list_params[2] is the alpha - it represents how much the cost of the 
				   path influences the chosen cell by the robot
	list_params[3] is the gamma - it represents how much the utility of 
				   the neighborood is reduced when a robot reaches a cell
	'''
	nrobots = int(round(list_params[0]))
	radar_radius = int(round(list_params[1]))
	alpha = list_params[2]
	gamma = list_params[3]
	
	fixed_params = {
		"nrobots": nrobots,
		"radar_radius": radar_radius, 
		"ncells": 5, 
		"obstacles_dist": 0.01, 
		"wifi_range": 3, 
		"alpha": alpha,
		"gamma" : gamma,
		"ninjured": 4,
		"dump_datas": False,
		"optimization_task": True,
		"load_file" : ""
	}

	print(str(list_params[0]) + " " + str(list_params[1]) + " " + str(list_params[2]) + " " + str(list_params[3]))

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
	run_data = batch_run.get_model_vars_dataframe() # it is actually one row
	return run_data["step"].iloc[0] + (run_data["total_idling"].iloc[0] / nrobots)

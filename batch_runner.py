from mesa.batchrunner import BatchRunner
from robot_exploration.model import ExplorationArea

fixed_params = {
	"nrobots": 5,
	"radar_radius": 3, 
	"ncells": 5, 
	"obstacles_dist": 0.01, 
	"wifi_range": 10, 
	"alpha": 0.1
}

batch_run = BatchRunner(
	ExplorationArea,
	None,
	fixed_params,
	iterations = 1,
	max_steps = 10000,
	model_reporters = None
)

batch_run.run_all()
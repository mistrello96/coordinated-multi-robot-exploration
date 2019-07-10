from .model import ExplorationArea
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
## Parameters of the model
# can be accessed in model Class using self
model_params = {
# order is default, min, max, step
    "nrobots": UserSettableParameter('slider', "Number of agents", 5, 1, 100, 1,
                                        description="Choose how many agents to include in the model"),
    "radar_radius":UserSettableParameter('slider', "Sensor radius", 1, 0, 10, 1,
                                        description="Choose how many cells around the robot can see"),
    "ncells":UserSettableParameter('number', "Number of rows/columns of cells", value=100),
    "obstacles_dist": UserSettableParameter('slider', "Obstacle probability", 0.1, 0, 1, 0.01,
                                        description="Choose how many obstacle there are in the map"),
    "wifi_range":UserSettableParameter('slider', "Wifi range", 50, 10, 1000, 10,
                                        description="Choose how many cells around the robot can see"),
    "alpha":UserSettableParameter('number', "Alpha value", value = 1,
                                        description="Importance of utility in target selection"),
    "gamma":UserSettableParameter('number', "Gamma value", value = 0.01,
                                        description="Importance of path cost in target selection")
}

#server = ModularServer(ExplorationArea, [grid, chart], "Search and Rescue simulation", model_params)
server = ModularServer(ExplorationArea, "Search and Rescue simulation", model_params)
server.port = 8521
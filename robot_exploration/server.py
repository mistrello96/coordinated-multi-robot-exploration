from .model import *
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import CanvasGrid

def agent_portrayal(agent):
    if type(agent) is Exploration:
        if agent.status == -1 :
            portrayal = {"Shape": "circle", "Color": "black", "Filled": "false", "Layer": 0, "r": 0.8}
        if agent.status == 0 :
            portrayal = {"Shape": "circle", "Color": "red", "Filled": "false", "Layer": 0, "r": 0.8}
        if agent.status == 1 :
            portrayal = {"Shape": "circle", "Color": "orange", "Filled": "false", "Layer": 0, "r": 0.8}
        if agent.status == 2 :
            portrayal = {"Shape": "circle", "Color": "green", "Filled": "false", "Layer": 0, "r": 0.8}
    else:
        if agent.exploration_status != 0:
            portrayal = {"Shape": "circle", "Color": "blue", "Filled": "true", "Layer": 0.5, "r": 0.4}
        else:
            portrayal = {"Shape": "circle", "Color": "gray", "Filled": "true", "Layer": 0.5, "r": 0.4}
    return portrayal

## Parameters of the model
# can be accessed in model Class using self
model_params = {
# order is default, min, max, step
    "nrobots": UserSettableParameter('slider', "Number of agents", 5, 1, 100, 1,
                                        description="Choose how many agents to include in the model"),
    "radar_radius":UserSettableParameter('slider', "Radar radius", 3, 0, 10, 1,
                                        description="Choose how many cells around the robot can see"),
    "ncells":UserSettableParameter('number', "Number of rows/columns of cells", value=10),
    "obstacles_dist": UserSettableParameter('slider', "Obstacle probability", 0.1, 0, 1, 0.01,
                                        description="Choose how many obstacle there are in the map"),
    "wifi_range":UserSettableParameter('slider', "Wifi range", 50, 10, 1000, 10,
                                        description="Choose how many cells around the robot can see"),
    "alpha":UserSettableParameter('number', "Alpha value", value = 0.01,
                                        description="Importance of path cost in target selection")
}

grid = CanvasGrid(agent_portrayal, 10, 10, 500, 500)

#server = ModularServer(ExplorationArea, [grid, chart], "Search and Rescue simulation", model_params)
server = ModularServer(ExplorationArea, [grid], "Search and Rescue simulation", model_params)
server.port = 8521
server.launch()
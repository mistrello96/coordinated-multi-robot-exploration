from .model import *

from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import CanvasGrid

def agent_portrayal(agent):
	# if cell, represent the corresponding colour
    if type(agent) is Cell:
        if agent.explored == -1 :
            portrayal = {"Shape": "rect", "Color": "black", "Filled": "false", "Layer": 0, "w": 1, "h" : 1}
        if agent.explored == 0 :
            portrayal = {"Shape": "rect", "Color": "red", "Filled": "false", "Layer": 0, "w": 1, "h" : 1}
        if agent.explored == 1 :
            portrayal = {"Shape": "rect", "Color": "orange", "Filled": "false", "Layer": 0, "w": 1, "h" : 1}
        if agent.explored == 2 :
            portrayal = {"Shape": "rect", "Color": "green", "Filled": "false", "Layer": 0, "w": 1, "h" : 1}
        if agent.explored == -2 or agent.explored == 42: # border print
            portrayal = {"Shape": "rect", "Color": "white", "Filled": "false", "Layer": 0, "w": 1, "h" : 1}
        if agent.priority and agent.explored == 0:
            portrayal = {"Shape": "rect", "Color": "brown", "Filled": "false", "Layer": 0, "w": 1, "h" : 1}
        if agent.wifi_bean:
            portrayal = {"Shape": "circle", "Color": "yellow", "Filled": "false", "Layer": 1, "r": 0.4}
    # if robot, represent corresponding status
    else:
        if agent.exploration_status != 0:
            portrayal = {"Shape": "circle", "Color": "blue", "Filled": "true", "Layer": 0.5, "r": 0.6}
        else:
            portrayal = {"Shape": "circle", "Color": "#505050", "Filled": "true", "Layer": 0.5, "r": 0.6}
    return portrayal

## Parameters of the model
model_params = {
# order of values is default, min, max, step
    "nrobots": UserSettableParameter('slider', "Number of agents", 5, 1, 100, 1,
                                        description = "Choose how many agents to include in the model"),
    "radar_radius": UserSettableParameter('slider', "Radar radius", 3, 0, 10, 1,
                                        description = "Choose how many cells around the robot can see"),
    "ncells": UserSettableParameter('number', "Number of rows/columns of cells", value = 10),
    "obstacles_dist": UserSettableParameter('slider', "Obstacle probability", 0.1, 0, 1, 0.01,
                                        description = "Choose how many obstacle there are in the map"),
    "wifi_range": UserSettableParameter('slider', "Wifi range", 100, 10, 1000, 10,
                                        description = "Choose how many cells around the robot can see"),
    "alpha": UserSettableParameter('number', "Alpha value", value = 0.01,
                                        description = "Importance of path cost in target selection")
}

#grid representation
grid = CanvasGrid(agent_portrayal, 20, 20, 800, 800)

#server = ModularServer(ExplorationArea, [grid, chart], "Search and Rescue simulation", model_params)
server = ModularServer(ExplorationArea, [grid], "Search and Rescue simulation", model_params)
server.port = 8521
server.launch()
from .model import *

from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.modules import ChartModule

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
    if type(agent) is Robot:
        if agent.exploration_status != 0:
            portrayal = {"Shape": "circle", "Color": "blue", "Filled": "true", "Layer": 0.5, "r": 0.6}
        else:
            portrayal = {"Shape": "circle", "Color": "#505050", "Filled": "true", "Layer": 0.5, "r": 0.6}
    if type(agent) is Injured:
        portrayal = None
    return portrayal

## Parameters of the model
model_params = {
# order of values is default, min, max, step
# TODO: the default values should be infered by the server_grid file, in order to make the map visible
# at the launch, rember that the map has to more rows/columns than ncells to be explored
    "nrobots": UserSettableParameter('slider', "Number of robots", 3, 1, 100, 1,
                                        description = "Choose how many agents to include in the model"),
    "radar_radius": UserSettableParameter('slider', "Radar radius", 3, 0, 10, 1,
                                        description = "Choose how many cells around the robot can see"),
    "ncells": UserSettableParameter('number', "Number of rows/columns of cells", value = 10),
    "obstacles_dist": UserSettableParameter('slider', "Obstacle probability", 0.1, 0, 1, 0.01,
                                        description = "Choose how many obstacle there are in the map"),
    "wifi_range": UserSettableParameter('slider', "Wifi range", 3, 2, 150, 1,
                                        description = "Choose how many cells the wifi signal is propagated"),
    "alpha": UserSettableParameter('number', "Alpha value", value = 0.1,
                                        description = "Importance of path cost in target selection"),
    "ninjured": UserSettableParameter('slider', "Number of injured", 3, 1, 30, 1,
                                        description = "Choose how many injured are in the map")
}

#grid representation
with open("./robot_exploration/server_grid.txt") as f: # the path starts from the run.py directory not from this file directory
    l = f.readlines()
params = l[0].split()
grid = CanvasGrid(agent_portrayal, params[0], params[1], params[2], params[3])

exploratio_chart = ChartModule([{"Label": "explored",
                      "Color": "Black"}],
                    data_collector_name='dc_percentage_step')

robort_chart = ChartModule([{"Label": "idling", "Color": "#505050"}, {"Label" : "travelling", "Color" : "Blue"}, {"Label" : "exploring", "Color" : "Green"}, {"Label" : "deploying_bean", "Color" : "Yellow"}],
                    data_collector_name='dc_robot_status')

#server = ModularServer(ExplorationArea, [grid, chart], "Search and Rescue simulation", model_params)
server = ModularServer(ExplorationArea, [grid, exploratio_chart, robort_chart], "Search and Rescue simulation", model_params)
#server = ModularServer(ExplorationArea, [grid], "Search and Rescue simulation", model_params)
server.port = 8521
server.launch()
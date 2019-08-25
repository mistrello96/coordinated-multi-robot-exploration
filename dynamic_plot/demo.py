# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.graph_objs as go
import numpy as np

colors = ["blue", "red", "green", "orange", "purple", "brown", "darkblue", "forestgreen",
		  "black", "gold", "darkred"]
alphas = [0, 0.0001, 0.0005, 0.001, 0.005, 0.01, 0.05, 0.1, 1, 6, 10]
dict_alpha_steps = dict()
max_step = 0
for a in alphas:
	df = pd.read_csv("../robot_exploration/results/alpha_steps/alpha_steps{}.csv".format(a))
	df = df[df.cost != -1]
	steps = sorted(list(set(df["step"])))
	if max_step < steps[-1]:
		max_step = steps[-1]
	_, bins = np.histogram(steps, bins = int((steps[-1] - steps[0]) // 100), density = False)
	step_averagecost = dict()
	for i in range(len(bins) - 2):
		m = (bins[i] + bins[i + 1]) / 2
		rows = df.loc[(df["step"] >= bins[i]) & (df["step"] < bins[i + 1])]
		costs = rows["cost"].tolist()
		step_averagecost[m] = np.mean(costs)
	m = (bins[-2] + bins[-1]) / 2
	rows = df.loc[(df["step"] >= bins[-2]) & (df["step"] <= bins[-1])]
	costs = rows["cost"].tolist()
	step_averagecost[m] = np.mean(costs)
	dict_alpha_steps[a] = (list(step_averagecost.keys()), list(step_averagecost.values()))

g_colors = ["blue", "red", "green", "orange", "purple", "brown"]
gammas = [0, 0.01, 0.1, 0.32, 0.65, 1]
dict_gamma_low = dict()
for g in gammas:
	df = pd.read_csv("../robot_exploration/results/gamma_variations_low_alpha/gamma_variation{}.csv".format(g))
	(vs, bins) = np.histogram(df["mean"], bins = int(round(max(df["mean"]) - min(df["mean"]))), density = False)
	ms = list()
	for i in range(len(bins) - 1):
		ms.append((bins[i] + bins[i + 1]) / 2)		
	dict_gamma_low[g] = (ms, vs)

dict_gamma_high = dict()
for g in gammas:
	df = pd.read_csv("../robot_exploration/results/gamma_variations_high_alpha/gamma_variation{}.csv".format(g))
	(vs, bins) = np.histogram(df["mean"], bins = int(round(max(df["mean"]) - min(df["mean"]))), density = False)
	ms = list()
	for i in range(len(bins) - 1):
		ms.append((bins[i] + bins[i + 1]) / 2)		
	dict_gamma_high[g] = (ms, vs)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets = external_stylesheets)

app.title = 'Coordinated multi-robot exploration'

app.layout = html.Div(children = [
    html.H1(children = 'Coordinated multi-robot exploration'),
    dcc.Tabs(id = 'tabs', children = [
        dcc.Tab(label = 'Average cost of chosen path over time', children = [
            html.Div([
                dcc.Graph(
                    id = 'alpha_steps',
                    figure = {
                        'data': [
                            go.Scatter(
                                x = dict_alpha_steps[a][0],
                                y = dict_alpha_steps[a][1],
                                text = ["Around step {}, average cost: {}". format(int(x), round(y, 3)) for x, y in zip(dict_alpha_steps[a][0], dict_alpha_steps[a][1])],
                                mode ='lines',
                                opacity = 0.8,
                                marker = {
                                    'color': color,
                                    'size': 15,
                                    'line': {'width': 2, 'color': color}
                                },
                                hoverinfo = 'text',
                                name = a
                            ) for a, color in zip(alphas, colors)
                        ],
                        'layout': go.Layout(
                            title = "Average cost of chosen path over time",
                            font = {'size': 14},
                            autosize = False,
                            width = 1890,
                            height = 750,
                            xaxis = {'title': "Step", 'showgrid': True, 'showline': True},
                            yaxis = {'title': "Cost of chosen path", 'showgrid': True},
                            margin={'l': 80, 'b': 40, 't': 45, 'r': 10},
                            legend={'x': 0.95, 'y': 0.95},
                            hovermode = 'closest'
                        )
                    }
                )
            ]),
        ]),

        dcc.Tab(label = 'Distribution of average distance between robots - low alpha', children = [
            html.Div([
                dcc.Graph(
                    id = 'gamma_low',
                    figure = {
                        'data': [
                            go.Scatter(
                                x = dict_gamma_low[g][0],
                                y = dict_gamma_low[g][1],
                                text = ["Distance: {}, steps: {}". format(int(x), round(y, 3)) for x, y in zip(dict_gamma_low[g][0], dict_gamma_low[g][1])],
                                mode ='lines',
                                opacity = 0.8,
                                marker = {
                                    'color': color,
                                    'size': 15,
                                    'line': {'width': 2, 'color': color}
                                },
                                hoverinfo = 'text',
                                name = g
                            ) for g, color in zip(gammas, g_colors)
                        ],
                        'layout': go.Layout(
                            title = "Distribution of average distance between robots",
                            font = {'size': 14},
                            autosize = False,
                            width = 1890,
                            height = 750,
                            xaxis = {'title': "Distance", 'showgrid': True, 'showline': True},
                            yaxis = {'title': "Number of steps", 'showgrid': True},
                            margin={'l': 80, 'b': 40, 't': 45, 'r': 10},
                            legend={'x': 0.95, 'y': 0.95},
                            hovermode = 'closest'
                        )
                    }
                )
            ]),
        ]),

        dcc.Tab(label = 'Distribution of average distance between robots - high alpha', children = [
            html.Div([
                dcc.Graph(
                    id = 'gamma_high',
                    figure = {
                        'data': [
                            go.Scatter(
                                x = dict_gamma_high[g][0],
                                y = dict_gamma_high[g][1],
                                text = ["Distance: {}, steps: {}". format(int(x), round(y, 3)) for x, y in zip(dict_gamma_high[g][0], dict_gamma_high[g][1])],
                                mode ='lines',
                                opacity = 0.8,
                                marker = {
                                    'color': color,
                                    'size': 15,
                                    'line': {'width': 2, 'color': color}
                                },
                                hoverinfo = 'text',
                                name = g
                            ) for g, color in zip(gammas, g_colors)
                        ],
                        'layout': go.Layout(
                            title = "Distribution of average distance between robots",
                            font = {'size': 14},
                            autosize = False,
                            width = 1890,
                            height = 750,
                            xaxis = {'title': "Distance", 'showgrid': True, 'showline': True},
                            yaxis = {'title': "Number of steps", 'showgrid': True},
                            margin={'l': 80, 'b': 40, 't': 45, 'r': 10},
                            legend={'x': 0.95, 'y': 0.95},
                            hovermode = 'closest'
                        )
                    }
                )
            ]),
        ])
    ])
])

if __name__ == '__main__':
    app.run_server(debug = False)
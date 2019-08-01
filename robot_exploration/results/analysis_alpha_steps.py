import pandas as pd
import matplotlib.pyplot as plt
import sys
import numpy as np

if __name__ == "__main__":
	assert len(sys.argv) == 2
	file = sys.argv[1] # ready for format


	colors = ["blue", "red", "green", "orange", "purple", "brown", "darkblue", "forestgreen",
			  "silver", "gold", "darkred"]
	alphas = [0, 0.0001, 0.0005, 0.001, 0.005, 0.01, 0.05, 0.1, 1, 6, 10]

	for a, color in zip(alphas, colors):
		df = pd.read_csv(file.format(a))

		df = df[df.cost != -1] # faster than drop according to stckoverflow

		steps = sorted(list(set(df["step"])))
		_, bins = np.histogram(steps, bins = int((steps[-1] - steps[0]) // 100), density = False)
		print(bins)
		step_averagecost = dict()
		step_stdcost = dict()
		for i in range(len(bins) - 2):
			m = (bins[i] + bins[i + 1]) / 2
			rows = df.loc[(df["step"] >= bins[i]) & (df["step"] < bins[i + 1])]
			costs = rows["cost"].tolist()
			step_averagecost[m] = np.mean(costs)
			step_stdcost[m] = np.std(costs)
		# the last bin has the interval closed do right too
		m = (bins[-2] + bins[-1]) / 2
		rows = df.loc[(df["step"] >= bins[-2]) & (df["step"] <= bins[-1])]
		costs = rows["cost"].tolist()
		step_averagecost[m] = np.mean(costs)
		step_stdcost[m] = np.std(costs)

		plt.figure(figsize = (8, 6), dpi = 300)
		plt.errorbar(step_averagecost.keys(), step_averagecost.values(), 
					 linestyle = "-", marker = '.',
					 yerr = step_stdcost.values(), color = color, 
					 markersize = 10, ecolor = "black", elinewidth = 1.5, 
					 barsabove = False)
		for s in step_stdcost.keys():
			plt.scatter([s, s], [step_averagecost[s] - step_stdcost[s], step_averagecost[s] + step_stdcost[s]], 
						marker = '_', s = 30, color = "black")
		
		plt.xlim(left = -1)
		ticks = [x for x in range(0, steps[-1], steps[-1] // 10)]
		plt.xticks(ticks, label = ticks, fontsize = 12)
		plt.yticks(fontsize = 12)
		plt.xlabel("Step", fontsize = 15)
		plt.ylabel("Cost of chosen path", fontsize = 15)
		plt.title("Average cost of the chosen path over the steps with an alpha value = {}".format(a))
		plt.tight_layout()
		plt.savefig("./alpha_steps/images/png/cost_alpha_{}.png".format(a))
		plt.savefig("./alpha_steps/images/pdf/cost_alpha_{}.pdf".format(a))
		plt.close()

	# comparison
	plt.figure(figsize = (8, 6), dpi = 300)
	max_step = 0
	for a, color in zip(alphas, colors):
		df = pd.read_csv(file.format(a))

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
			step_stdcost[m] = np.std(costs)
		# the last bin has the interval both sides closed
		m = (bins[-2] + bins[-1]) / 2
		rows = df.loc[(df["step"] >= bins[-2]) & (df["step"] <= bins[-1])]
		costs = rows["cost"].tolist()
		step_averagecost[m] = np.mean(costs)

		plt.plot(list(step_averagecost.keys()), list(step_averagecost.values()),
				 color = color, label = "alpha = {}".format(a))
	
	plt.xlim(left = -1)
	ticks = [x for x in range(0, max_step, max_step // 10)]
	plt.xticks(ticks, label = ticks, fontsize = 12)
	plt.yticks(fontsize = 12)
	plt.xlabel("Step", fontsize = 15)
	plt.ylabel("Cost of chosen path", fontsize = 15)
	plt.title("Average cost of the chosen path varying alpha")
	plt.legend()
	plt.tight_layout()
	plt.savefig("./alpha_steps/images/png/comparison.png")
	plt.savefig("./alpha_steps/images/pdf/comparison.pdf")
	plt.close()	
import pandas as pd
import matplotlib.pyplot as plt
import sys
import numpy as np

if __name__ == "__main__":
	assert len(sys.argv) == 3
	file = sys.argv[1]
	output_file = sys.argv[2] # name ready for the format 

	# for over the alpha values of different files
	df = pd.read_csv(file)

	df = df[df.cost != -1] # faster than drop according to stckoverflow
	
	step_averagecost = dict()
	step_stdcost = dict()
	steps = sorted(list(set(df["step"])))
	for s in steps:
		rows = df.loc[df["step"] == s]
		costs = rows["cost"].tolist()
		step_averagecost[s] = np.mean(costs)
		step_stdcost[s] = np.std(costs)
	plt.figure(figsize = (8, 6), dpi = 300)
	plt.errorbar(step_averagecost.keys(), step_stdcost.values(), 
				 linestyle = "-", marker = '.',
				 yerr = step_stdcost.values(), color = "red", 
				 markersize = 10, ecolor = "black", elinewidth = 1.5, 
				 barsabove = False)
	for s in step_stdcost.keys():
		plt.scatter([s, s], [step_averagecost[s] - step_stdcost[s], step_averagecost[s] + step_stdcost[s]], 
					marker = '_', s = 40, color = "black")
	plt.xlim(left = - 1)
	plt.xticks(fontsize = 12)
	plt.yticks(fontsize = 12)
	plt.xlabel("Step", fontsize = 15)
	plt.ylabel("Cost of chosen path", fontsize = 15)
	# plt.title("Average cost of the chosen path over the steps with an alpha value = {}".format(a))
	plt.title("test")
	plt.tight_layout()
	# plt.savefig("./".format(a))
	# plt.savefig("./".format(a))
	plt.savefig("test.png")
	plt.close()
import pandas as pd
import matplotlib.pyplot as plt
import sys
import numpy as np

if __name__ == "__main__":
	assert len(sys.argv) == 4
	file = sys.argv[1]
	path = sys.argv[2] # path before the divsion in png or pdf
	output_file = sys.argv[3] # further subdirectories and file name

	df = pd.read_csv(file)

	simulations = sorted(list(set(df["sim_id"])))
	number_of_simulations = len(simulations)
	print(number_of_simulations)
	
	for s in simulations:
		tmp_df = df.loc[df["sim_id"] == s]
		
		steps = sorted(list(set(tmp_df["step"])))
		_, bins = np.histogram(steps, bins = int((steps[-1] - steps[0]) // 100), density = False)
		idling_mean = dict()
		idling_std = dict()
		travelling_mean = dict()
		travelling_std = dict()
		exploring_mean = dict()
		exploring_std = dict()
		deploying_mean = dict()
		deploying_std = dict()
		for i in range(len(bins) - 2):
			m = (bins[i] + bins[i + 1]) / 2
			rows = tmp_df.loc[(tmp_df["step"] >= bins[i]) & (tmp_df["step"] < bins[i + 1])]

			idling = tmp_df["idling"].tolist()
			idling_mean[m] = np.mean(idling)
			idling_std[m] = np.std(idling)

			travelling = tmp_df["travelling"].tolist()
			travelling_mean[m] = np.mean(travelling)
			travelling_std[m] = np.std(travelling)
			
			exploring = tmp_df["exploring"].tolist()
			exploring_mean[m] = np.mean(exploring)
			exploring_std[m] = np.std(exploring)

			deploying_bean = tmp_df["deploying_bean"].tolist()
			deploying_mean[m] = np.mean(deploying_bean)
			deploying_std[m] = np.std(deploying_bean)

		# the last bin has the interval closed do right too
		m = (bins[-2] + bins[-1]) / 2
		rows = tmp_df.loc[(tmp_df["step"] >= bins[-2]) & (tmp_df["step"] <= bins[-1])]
		
		idling = tmp_df["idling"].tolist()
		idling_mean[m] = np.mean(idling)
		idling_std[m] = np.std(idling)

		travelling = tmp_df["travelling"].tolist()
		travelling_mean[m] = np.mean(travelling)
		travelling_std[m] = np.std(travelling)
			
		exploring = tmp_df["exploring"].tolist()
		exploring_mean[m] = np.mean(exploring)
		exploring_std[m] = np.std(exploring)

		deploying_bean = tmp_df["deploying_bean"].tolist()
		deploying_mean[m] = np.mean(deploying_bean)
		deploying_std[m] = np.std(deploying_bean)

		plt.figure(figsize = (8, 6), dpi = 300)
		'''
		plt.plot(steps, idling, linestyle = '-',
				 color = "darkred", label = "idling")
		plt.plot(steps, travelling, linestyle = '-',
				 color = "darkblue", label = "travelling")
		plt.plot(steps, exploring, linestyle = '-',
				 color = "darkgreen", label = "exploring")
		plt.plot(steps, deploying_bean, linestyle = '-',
				 color = "darkorange", label = "deploying_bean")
		'''

		plt.errorbar(idling_mean.keys(), idling_mean.values(), 
					 linestyle = "-", marker = '.',
					 yerr = idling_std.values(), color = "darkred", 
					 markersize = 10, ecolor = "black", elinewidth = 1.5, 
					 barsabove = False, label = "idling")
		for m in idling_mean.keys():
			plt.scatter([m, m], [idling_mean[m] - idling_std[m], idling_mean[m] + idling_std[m]], 
						marker = '_', s = 30, color = "black")

		plt.errorbar(travelling_mean.keys(), travelling_mean.values(), 
					 linestyle = "-", marker = '.',
					 yerr = travelling_std.values(), color = "darkblue", 
					 markersize = 10, ecolor = "black", elinewidth = 1.5, 
					 barsabove = False, label = "travelling")
		for m in travelling_mean.keys():
			plt.scatter([m, m], [travelling_mean[m] - travelling_std[m], travelling_mean[m] + travelling_std[m]], 
						marker = '_', s = 30, color = "black")

		plt.errorbar(exploring_mean.keys(), exploring_mean.values(), 
					 linestyle = "-", marker = '.',
					 yerr = exploring_std.values(), color = "darkgreen", 
					 markersize = 10, ecolor = "black", elinewidth = 1.5, 
					 barsabove = False, label = "exploring")
		for m in exploring_mean.keys():
			plt.scatter([m, m], [exploring_mean[m] - exploring_std[m], exploring_mean[m] + exploring_std[m]], 
						marker = '_', s = 30, color = "black")

		plt.errorbar(deploying_mean.keys(), deploying_mean.values(), 
					 linestyle = "-", marker = '.',
					 yerr = deploying_std.values(), color = "darkorange", 
					 markersize = 10, ecolor = "black", elinewidth = 1.5, 
					 barsabove = False, label = "deploying bean")
		for m in deploying_mean.keys():
			plt.scatter([m, m], [deploying_mean[m] - deploying_std[m], deploying_mean[m] + deploying_std[m]], 
						marker = '_', s = 30, color = "black")

		plt.xlim(left = -0.5)
		plt.xticks(fontsize = 12)
		plt.yticks(fontsize = 12)
		plt.xlabel("Step", fontsize = 15)
		plt.ylabel("Number of robots", fontsize = 15)
		plt.title("Number of robots in a status for every step")
		plt.legend()
		plt.tight_layout()
		plt.savefig("{}/png/{}_sim{}.png".format(path, output_file, s))
		plt.savefig("{}/pdf/{}_sim{}.pdf".format(path, output_file, s))
		plt.close()
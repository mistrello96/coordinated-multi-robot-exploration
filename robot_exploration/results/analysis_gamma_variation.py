import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys
import random as rnd

if __name__ == "__main__":
	assert len(sys.argv) == 2
	# the file name should be ready to handle the format function
	# use the {} instead of the value of the gamma
	# same for outputfile
	file = sys.argv[1]

	rnd.seed()

	gammas = [0, 0.01, 0.1, 0.32, 0.65, 1]
	colors = ["blue", "red", "green", "orange", "purple", "brown"]

	for g, color in zip(gammas, colors):
		df = pd.read_csv(file.format(g))

		plt.figure(figsize = (8, 6), dpi = 300)
		plt.yscale("log")
		(vs, bins) = np.histogram(df["mean"], bins = int(round(max(df["mean"]) - min(df["mean"]))), density = False)
		print("bins for gamma {}: {} with number of bins {}".format(g, bins, len(bins) - 1))
		print(vs)

		for i in range(len(bins) - 1):
			m = (bins[i] + bins[i + 1]) / 2
			plt.scatter(m, vs[i], marker = '.', color = color, s = 50)
			'''
			rows = df.loc[(df["mean"] >= bins[i]) & (df["mean"] < bins[i + 1])]
			stds = rows["std"]
			mean_std = np.mean(stds)
			plt.errorbar(m, vs[i], yerr = mean_std, marker = '.', linestyle = None,
						 color = "red", markersize = 10, ecolor = "black", elinewidth = 1.5, 
						 barsabove = False)

			plt.scatter([m, m], [vs[i] - mean_std, vs[i] + mean_std], marker = '_',
						s = 40, color = "black")
			'''
		plt.xlim(left = bins[0] - 1)
		# plt.ylim(bottom = 0)
		plt.xticks(fontsize = 12)
		plt.yticks(fontsize = 12)
		plt.xlabel("Average distance", fontsize = 15)
		plt.ylabel("Number of steps", fontsize = 15)
		plt.title("Distribution of average distance with gamma value equals to {}".format(g))
		plt.tight_layout()
		plt.savefig("./gamma_variations/images/png/distribution_distance_gamma_{}.png".format(g))
		plt.savefig("./gamma_variations/images/pdf/distribution_distance_gamma_{}.pdf".format(g))
		plt.close()

		plt.figure(figsize = (8, 6), dpi = 300)
		sim_id = rnd.randint(0, 9)
		sim_df = df.loc[df["sim_id"] == sim_id]
		plt.plot(sim_df["step"], sim_df["mean"], linestyle = '-', 
				 linewidth = 2.5, color = 'black', label = "Average", antialiased = True)
		# Plot of standard deviation
		plt.plot(sim_df["step"], [m - s for m, s in zip(sim_df["mean"], sim_df["std"])],
				 color = 'red', linestyle = '-', linewidth = 0.2, antialiased = True)
		plt.plot(sim_df["step"], [m + s for m, s in zip(sim_df["mean"], sim_df["std"])],
				 color = 'red', linestyle = '-', linewidth = 0.2, antialiased = True)
		plt.fill_between(sim_df["step"], 
						 [m - s for m, s in zip(sim_df["mean"], sim_df["std"])],
						 [m + s for m, s in zip(sim_df["mean"], sim_df["std"])],
						 color = 'red', alpha = 0.5)
		plt.xlim(left = -0.5, right = max(sim_df["step"]) + 10)
		plt.xticks(fontsize = 12)
		plt.yticks(fontsize = 12)
		plt.xlabel("Step", fontsize = 15)
		plt.ylabel("Average distance between robots", fontsize = 15)
		plt.title("Evolution of distance between robots during the exploration")
		plt.tight_layout()
		plt.savefig("./gamma_variations/images/png/dinstance_simulation_gamma_{}_simid_{}.png".format(g,sim_id))
		plt.savefig("./gamma_variations/images/pdf/dinstance_simulation_gamma_{}_simid_{}.pdf".format(g,sim_id))
		plt.close()

	# aggregating results
	# in theory we could do that during the loop above changing the figure to work on
	# but for clarity we write that below
	plt.figure(figsize = (8, 6), dpi = 300)
	# plt.yscale("log")
	for g, color in zip(gammas, colors):
		df = pd.read_csv(file.format(g))

		(vs, bins) = np.histogram(df["mean"], bins = int(round(max(df["mean"]) - min(df["mean"]))), density = False)
		ms = list()
		for i in range(len(bins) - 1):
			ms.append((bins[i] + bins[i + 1]) / 2)		
		plt.plot(ms, vs, '-', color = color, antialiased = True,
				 label = "gamma = {}".format(g))
		'''
		rows = df.loc[(df["mean"] >= bins[i]) & (df["mean"] < bins[i + 1])]
		stds = rows["std"]
		mean_std = np.mean(stds)
		plt.errorbar(m, vs[i], yerr = mean_std, marker = '.', linestyle = None,
					 markersize = 10, ecolor = "black", elinewidth = 1.5, 
					 color = color, barsabove = False, 
					 label = "gamma = {}".format(g) if i == 0 else None)

		plt.scatter([m, m], [vs[i] - mean_std, vs[i] + mean_std], marker = '_',
					s = 40, color = "black")
		'''
	plt.xlim(left = bins[0] - 1)
	plt.xticks(fontsize = 12)
	plt.yticks(fontsize = 12)
	plt.xlabel("Average distance", fontsize = 15)
	plt.ylabel("Number of steps", fontsize = 15)
	plt.title("Comparison of distributions of average distance between robots")
	plt.legend()	
	plt.tight_layout()
	plt.savefig("./gamma_variations/images/png/comparison.png")
	plt.savefig("./gamma_variations/images/pdf/comparison.pdf")
	plt.close()

	# Aggregate all, we need a df containing all datas
	df = pd.read_csv(file.format(gammas[0]))
	for g in gammas[1:]:
		df = df.append(pd.read_csv(file.format(g)), ignore_index = True, sort = False)

	means_mean = list()
	means_std = list()
	maxs_std = list()
	for g in gammas:
		vs = df.loc[df["gamma"] == g]
		mean_mean = np.mean(vs["mean"])
		means_mean.append(mean_mean)

		mean_std = np.mean(vs["std"])
		means_std.append(mean_std)
		
		max_std = max(vs["std"])
		maxs_std.append(max_std)

	plt.figure(figsize = (8, 6), dpi = 300)
	plt.plot(gammas, means_mean, linestyle = '-', 
		linewidth = 2.5, color = 'black', label = "Average", antialiased = True)
	# Plot of standard deviation
	plt.plot(gammas, [m - s for m, s in zip(means_mean, means_std)],
			 color = 'red', linestyle = '-', linewidth = 0.2, antialiased = True,
			 label = "Average of standard deviation")
	plt.plot(gammas, [m + s for m, s in zip(means_mean, means_std)],
			 color = 'red', linestyle = '-', linewidth = 0.2, antialiased = True)
	plt.fill_between(gammas, 
					 [m - s for m, s in zip(means_mean, means_std)],
					 [m + s for m, s in zip(means_mean, means_std)],
					 color = 'red', alpha = 0.5)
	# Plot of maximum standard deviation
	plt.plot(gammas, [m - s for m, s in zip(means_mean, maxs_std)],
			 color = 'black', linestyle = '--', linewidth = 1.5, 
			 antialiased = True, label = "Maximum of standard deviation")
	plt.plot(gammas, [m + s for m, s in zip(means_mean, maxs_std)],
			 color = 'black', linestyle = '--', linewidth = 1.5, 
			 antialiased = True)

	plt.xlim(left = min(gammas) - 10e-3, right = max(gammas) + 1e-3)
	plt.xticks(gammas[1: ], label = gammas[1: ], fontsize = 12)
	plt.yticks(fontsize = 12)
	plt.xlabel("Gamma", fontsize = 15)
	plt.ylabel("Distance between robots", fontsize = 15)
	plt.title("How gamma infuences the distance between robots")
	plt.legend()
	plt.tight_layout()
	plt.savefig("./gamma_variations/images/png/gamma_vs_distance.png")
	plt.savefig("./gamma_variations/images/pdf/gamma_vs_distance.pdf")
	plt.close()

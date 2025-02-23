import pandas as pd
import matplotlib.pyplot as plt
import sys
import numpy as np

def plot_alphas(df, output_file, alpha_values, ticks_label):
	means_mean = list()
	means_std = list()
	maxs_std = list()
	for a in alpha_values:
		vs = df.loc[df["alpha"] == a]
		mean_mean = np.mean(vs["mean"])
		means_mean.append(mean_mean)

		mean_std = np.mean(vs["std"])
		means_std.append(mean_std)
		
		max_std = max(vs["std"])
		maxs_std.append(max_std)

	plt.figure(figsize = (8, 6), dpi = 300)
	plt.plot(alpha_values, means_mean, linestyle = '-', 
		linewidth = 2.5, color = 'black', label = "Average", antialiased = True)
	# Plot of standard deviation
	plt.plot(alpha_values, [m - s for m, s in zip(means_mean, means_std)],
			 color = 'red', linestyle = '-', linewidth = 0.2, antialiased = True,
			 label = "Average of standard deviation")
	plt.plot(alpha_values, [m + s for m, s in zip(means_mean, means_std)],
			 color = 'red', linestyle = '-', linewidth = 0.2, antialiased = True)
	plt.fill_between(alpha_values, 
					 [m - s for m, s in zip(means_mean, means_std)],
					 [m + s for m, s in zip(means_mean, means_std)],
					 color = 'red', alpha = 0.5)
	# Plot of maximum standard deviation
	plt.plot(alpha_values, [m - s for m, s in zip(means_mean, maxs_std)],
			 color = 'black', linestyle = '--', linewidth = 1.5, 
			 antialiased = True, label = "Maximum of standard deviation")
	plt.plot(alpha_values, [m + s for m, s in zip(means_mean, maxs_std)],
			 color = 'black', linestyle = '--', linewidth = 1.5, 
			 antialiased = True)

	plt.xlim(left = min(alpha_values),right = max(alpha_values))
	plt.xticks(ticks_label, labels = ticks_label, fontsize = 12)
	plt.yticks(fontsize = 12)
	plt.xlabel("Alpha", fontsize = 15)
	plt.ylabel("Cost of path chosen (# of steps)", fontsize = 15)
	plt.title("How alpha influences the path chosen")
	plt.legend()
	plt.tight_layout()
	plt.savefig("./images/png/{}.png".format(output_file))
	plt.savefig("./images/pdf/{}.pdf".format(output_file))
	plt.close()

if __name__ == "__main__":
	assert len(sys.argv) == 3
	file = sys.argv[1]
	output_file = sys.argv[2]

	df = pd.read_csv(file)

	alpha_values = sorted(list(set(df["alpha"])))
	ticks_label = [0, 1, 6, 10]
	plot_alphas(df, output_file + "_all", alpha_values,ticks_label)
	small_alphas = [a for a in alpha_values if a <= 0.1]
	ticks_label = [0, 0.01, 0.05, 0.1]
	plot_alphas(df, output_file + "_0_1", small_alphas, ticks_label)
	very_small_alphas = [a for a in alpha_values if a <= 0.005]
	ticks_label = [0, 1e-4, 5e-4, 1e-3, 5e-3]
	plot_alphas(df, output_file + "_0_005", very_small_alphas, ticks_label)	
import pandas as pd
import matplotlib.pyplot as plt
import sys
import numpy as np

if __name__ == "__main__":
	assert len(sys.argv) == 3
	file = sys.argv[1]
	output_file = sys.argv[2]

	df = pd.read_csv(file)

	alpha_values = sorted(list(set(df["alpha"])))

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
	plt.xscale("log")
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

	plt.xlim(left = min(alpha_values) - 10e-5, right = max(alpha_values))
	plt.xticks(alpha_values, labels = alpha_values, fontsize = 12)
	plt.yticks(fontsize = 12)
	plt.xlabel("Alpha", fontsize = 15)
	plt.ylabel("Cost of path chosen (# of steps)", fontsize = 15)
	plt.title("How alpha influences the path chosen")
	plt.legend()
	plt.tight_layout()
	plt.savefig("./images/png/{}.png".format(output_file))
	plt.savefig("./images/pdf/{}.pdf".format(output_file))
	plt.close()

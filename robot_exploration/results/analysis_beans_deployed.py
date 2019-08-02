import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys

if __name__ == "__main__":
	assert len(sys.argv) == 3
	file = sys.argv[1]
	plot_beans_deployed = sys.argv[2]

	df = pd.read_csv(file)

	# dimensions vs bean_deployed
	dimensions = sorted(list(set(df["ncells"])))
	mean_deployed = list()
	std_deployed = list()
	for k in dimensions:
		vs = df.loc[df["ncells"] == k]
		mean = np.mean(vs["beans_deployed"])
		std = np.std(vs["beans_deployed"])
		mean_deployed.append(mean)
		std_deployed.append(std)
	plt.figure(figsize = (8, 6), dpi = 300)
	plt.plot(dimensions, mean_deployed, linestyle = '-', 
		linewidth = 2.5, color = 'black', label = "Average", antialiased = True)
	plt.plot(dimensions, [m - s for m, s in zip(mean_deployed, std_deployed)],
			 color = 'red', linestyle = '-', linewidth = 0.2, antialiased = True)
	plt.plot(dimensions, [m + s for m, s in zip(mean_deployed, std_deployed)],
			 color = 'red', linestyle = '-', linewidth = 0.2, antialiased = True)
	plt.fill_between(dimensions, 
					 [m - s for m, s in zip(mean_deployed, std_deployed)],
					 [m + s for m, s in zip(mean_deployed, std_deployed)],
					 color = 'red', alpha = 0.5)
	plt.xlim(left = min(dimensions) - 1)
	plt.xticks(fontsize = 12)
	plt.yticks(fontsize = 12)
	plt.xlabel("Dimensions", fontsize = 15)
	plt.ylabel("Number of beans deployed", fontsize = 15)
	plt.title("Number of beans deployed for a NxN map")
	plt.legend()
	plt.tight_layout()
	plt.savefig("{}.png".format(plot_beans_deployed))
	plt.savefig("{}.pdf".format(plot_beans_deployed))
	plt.close()
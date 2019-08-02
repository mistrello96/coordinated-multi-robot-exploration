import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys

if __name__ == "__main__":

	df = pd.read_csv("./aggregate_csvs.csv")

	# nrobots vs bean_deployed
	nrobots = sorted(list(set(df["nrobots"])))
	mean_deployed = list()
	std_deployed = list()
	for k in nrobots:
		vs = df.loc[df["nrobots"] == k]
		mean = np.mean(vs["beans_deployed"])
		std = np.std(vs["beans_deployed"])
		mean_deployed.append(mean)
		std_deployed.append(std)
	plt.figure(figsize = (8, 6), dpi = 300)
	plt.plot(nrobots, mean_deployed, linestyle = '-', 
		linewidth = 2.5, color = 'black', label = "Average", antialiased = True)
	plt.plot(nrobots, [m - s for m, s in zip(mean_deployed, std_deployed)],
			 color = 'red', linestyle = '-', linewidth = 0.2, antialiased = True)
	plt.plot(nrobots, [m + s for m, s in zip(mean_deployed, std_deployed)],
			 color = 'red', linestyle = '-', linewidth = 0.2, antialiased = True)
	plt.fill_between(nrobots, 
					 [m - s for m, s in zip(mean_deployed, std_deployed)],
					 [m + s for m, s in zip(mean_deployed, std_deployed)],
					 color = 'red', alpha = 0.5)
	plt.xlim(left = min(nrobots) - 0.5, right = max(nrobots) + 0.5)
	plt.xticks(fontsize = 12)
	plt.yticks(fontsize = 12)
	plt.xlabel("Number of robots", fontsize = 15)
	plt.ylabel("Number of beans deployed", fontsize = 15)
	plt.title("Number of beans deployed varying the number of robots ona given map")
	plt.legend()
	plt.tight_layout()
	plt.savefig("./images/png/robots_beans.png")
	plt.savefig("./images/pdf/robots_beans.pdf")
	plt.close()
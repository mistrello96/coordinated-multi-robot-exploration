import pandas as pd
import matplotlib.pyplot as plt
import sys

if __name__ == "__main__":
	assert len(sys.argv) == 3
	file = sys.argv[1]
	output_file = sys.argv[2]

	df = pd.read_csv(file)

	nrobots = sorted(list(set(df["nrobots"])))
	fitness_mean = dict()
	fitness_std = dict()
	for r in nrobots:
		rows = df.loc[df["nrobots"] == r]
		fitnesses = rows["fitness"].tolist()
		fitness_mean[r] = np.mean(fitnesses)
		fitness_std[r] = np.std(fitnesses)

	plt.figure(figsize = (8, 6), dpi = 300)
	plt.errorbar(fitness_mean.keys(), fitness_mean.values(), 
				 linestyle = "-", marker = '.',
				 yerr = fitness_std.values(), color = "red", 
				 markersize = 10, ecolor = "black", elinewidth = 1.5, 
				 barsabove = False)
	for r in fitness_std.keys():
		plt.scatter([r, r], [fitness_mean[s] - fitness_std[s], fitness_mean[s] + fitness_std[s]], 
					marker = '_', s = 30, color = "black")
	
	plt.xlim(left = -1)
	ticks = [x for x in range(0, nrobots[-1], nrobots[-1] // 10)]
	plt.xticks(ticks, label = ticks, fontsize = 12)
	plt.yticks(fontsize = 12)
	plt.xlabel("Number of robots", fontsize = 15)
	plt.ylabel("Fitness", fontsize = 15)
	plt.title("Evolution of fitness given the number of robots")
	plt.tight_layout()
	plt.savefig("./images/png/{}.png".format(output_file))
	plt.savefig("./images/pdf/{}.pdf".format(output_file))
	plt.close()
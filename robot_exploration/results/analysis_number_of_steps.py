import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys

if __name__ == "__main__":
	assert len(sys.argv) == 3
	file = sys.argv[1]
	nrobots = sys.argv[2]

	df = pd.read_csv(file)

	# exploration time required vs number of steps, same number of robots
	plt.figure(figsize = (8, 6), dpi = 300)
	# for the same estimated time there can be more than one value of steps 
	# required.
	plt.plot(df["total_exploration_time_required"], df["steps"],
			 '-', color = "black")
	plt.xlim(left = min(df["total_exploration_time_required"]) - 5)
	plt.xticks(fontsize = 12)
	plt.yticks(fontsize = 12)
	plt.xlabel("Estimated time of exploration (# of ticks)", fontsize = 15)
	plt.ylabel("Time required for exploration (# of ticks)", fontsize = 15)
	plt.title("Minimum time required to explore vs actual time taken")
	plt.tight_layout()
	plt.savefig("./images/png/time_required_vs_taken_{}.png".format(nrobots))
	plt.savefig("./images/pdf/time_required_vs_taken_{}.pdf".format(nrobots))
	plt.close()

	# dimensions vs bean_deployed
	dimensions = set(df["ncells"])
	mean_deployed = {k: v}
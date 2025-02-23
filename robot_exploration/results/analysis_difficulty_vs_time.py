import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys

if __name__ == "__main__":
	assert len(sys.argv) == 4
	file = sys.argv[1]
	path = sys.argv[2] # path before the divsion in png or pdf, no last /
	plot_difficulty_vs_steps = sys.argv[3] # further subdirectories and file name

	df = pd.read_csv(file)

	# exploration time required vs number of steps, same number of robots
	plt.figure(figsize = (8, 6), dpi = 300)
	# for the same estimated time there can be more than one value of steps 
	# required.
	plt.plot(df["total_difficulty"], df["steps"],
			 '-', color = "black")
	plt.xlim(left = min(df["total_difficulty"]) - 5)
	plt.xticks(fontsize = 12)
	plt.yticks(fontsize = 12)
	plt.xlabel("Total difficulty", fontsize = 15)
	plt.ylabel("Time required for exploration (# of steps)", fontsize = 15)
	plt.title("Total difficulty vs actual time taken")
	plt.tight_layout()
	plt.savefig("{}/png/{}.png".format(path, plot_difficulty_vs_steps))
	plt.savefig("{}/pdf/{}.pdf".format(path, plot_difficulty_vs_steps))
	plt.close()
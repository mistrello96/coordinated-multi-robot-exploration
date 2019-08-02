import pandas as pd
import matplotlib.pyplot as plt
import sys
import numpy as np

if __name__ == "__main__":
	assert len(sys.argv) == 3
	file = sys.argv[1]
	output_file = sys.argv[2]

	df = pd.read_csv(file)

	simulations = set(df["sim_id"])
	number_of_simulations = len(simulations)

	if number_of_simulations == 1:
		plt.figure(figsize = (8, 6), dpi = 300)
		plt.plot(df["step"], round(df["explored"], 2),
				 '-', color = "black")
		plt.xlim(left = -0.5)
		plt.xticks(fontsize = 12)
		plt.yticks(fontsize = 12)
		plt.xlabel("Step", fontsize = 15)
		plt.ylabel("Area explored (%)", fontsize = 15)
		plt.title("Area explored at every step of simulation")
		plt.tight_layout()
		plt.savefig("./images/png/{}.png".format(output_file))
		plt.savefig("./images/pdf/{}.pdf".format(output_file))
		plt.close()
		return
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
		steps = df["step"].tolist()
		idling = df["idling"].tolist()
		travelling = df["travelling"].tolist()
		exploring = df["exploring"].tolist()
		deploying_bean = df["deploying_bean"].tolist()

		plt.figure(figsize = (8, 6), dpi = 300)
		plt.plot(steps, idling, linestyle = '-',
				 color = "darkred", label = "idling")
		plt.plot(steps, travelling, linestyle = '-',
				 color = "darkblue", label = "travelling")
		plt.plot(steps, exploring, linestyle = '-',
				 color = "darkgreen", label = "exploring")
		plt.plot(steps, deploying_bean, linestyle = '-',
				 color = "darkorange", label = "deploying_bean")

		plt.xlim(left = -0.5)
		plt.xticks(fontsize = 12)
		plt.yticks(fontsize = 12)
		plt.xlabel("Step", fontsize = 15)
		plt.ylabel("Number of robots", fontsize = 15)
		plt.title("Number of robots in a status for every step")
		plt.legend()
		plt.tight_layout()
		plt.savefig("./images/png/{}.png".format(output_file))
		plt.savefig("./images/pdf/{}.pdf".format(output_file))
		plt.close()

	# as for percentage exploration, how to handle multiple simulations
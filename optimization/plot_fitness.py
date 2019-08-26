import matplotlib.pyplot as plt

if __name__ == "__main__":
	with open("best_fitness.txt") as f:
		rows = f.readlines()
	values = []
	for r in rows[: -1]:
		r = r.rstrip()
		values.append(round(float(r), 3))

	plt.figure(figsize = (8, 6), dpi = 300)
	plt.plot(range(0, len(values)), values,
			 '-', color = "black")
	plt.xlim(left = 0, right = len(rows))
	plt.xticks(fontsize = 12)
	plt.yticks(fontsize = 12)
	plt.xlabel("Iteration", fontsize = 15)
	plt.ylabel("Fitness", fontsize = 15)
	plt.title("Evolution of optimal fitness")
	plt.tight_layout()
	plt.savefig("optimal_fitness.png")
	plt.savefig("optimal_fitness.pdf")
	plt.close()
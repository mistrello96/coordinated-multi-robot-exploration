import pandas as pd
import matplotlib.pyplot as plt
import nuumpy as np
import sys

if __name__ == "__main__":
	assert len(sys.argv) == 3
	file = sys.argv[1]
	output_file = sys.argv[2]

	df = pd.read_csv(file)

	
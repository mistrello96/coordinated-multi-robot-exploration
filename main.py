from batch_runner import fitness
from fstpso import FuzzyPSO

if __name__ == "__main__":
	dump_best_fitness = "./optimization/best_fitness.txt"
	dump_best_solution = "./optimization/best_solution.txt"

	FP = FuzzyPSO()
	'''
	list_params[0] is the number of the robots which has to be an integer
	list_params[1] is the radar radius which has to be an integer
	list_params[2] is the alpha - it represents how much the cost of the 
				   path influences the chosen cell by the robot
	list_params[3] is the gamma - it represents how much the utility of 
				   the neighborood is reduced when a robot reaches a cell
	
	Please, note that the cast to integer is done in the fitness function
	'''
	FP.set_search_space([[1, 15], [1, 10], [0.001, 10], [0, 1]])
	FP.set_fitness(fitness, skip_test = False)
	result =  FP.solve_with_fstpso(dump_best_fitness = dump_best_fitness, 
								   dump_best_solution = dump_best_solution)
	print("Best solution: " + str(result[0]))
	print("Whose fitness is: " + str(result[1]))
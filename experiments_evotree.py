# Authors: Paweł Kochański, Jakub Proboszcz
# Written as a part of project in course UMA in semester 23Z

from evo_tree import EvoTree
from random import seed
from helpers import cross_validate, prepare_datasets
from multiprocessing import Process
from reproduction import *
from succession import *


# Script executes hyperparameter grid search for tree evolution algorithm.


POPULATION_SIZE = 20
MAX_ITERATIONS = 500

def leaf_probability(depth):
    return 1 - (0.5 ** depth)


reproductions = [
    proportional_reproduction,
    lambda population, fitnesses: rank_reproduction(
        population, fitnesses, 0.01, get_k_from_a(0.01, POPULATION_SIZE)),
    lambda population, fitnesses: truncation_reproduction(
        population, fitnesses, 0.8),
    lambda population, fitnesses: tournament_reproduction(
        population, fitnesses, 2),
]

successions = [
    generational_succession,
    lambda population, genetic_operations_population, scores, genetic_operations_scores: elite_succession(
        population, genetic_operations_population, scores, genetic_operations_scores, 2),
]


def run_experiment(name, data, counters, file_lengths):
    for seed_nr in range(5):
        for max_depth in [5, 20]:
            for j, reproduction in enumerate(reproductions):
                for mutation_probability in [0.4, 0.8]:
                    for leaf_inner_swap_probabilty in [0, 0.3]:
                        for crossover_probability in [0, 0.4]:
                            for k, succession in enumerate(successions):
                                counters[name] += 1
                                if counters[name] <= file_lengths[name]:
                                    continue

                                seed(seed_nr)

                                model = EvoTree(POPULATION_SIZE, max_depth, leaf_probability, MAX_ITERATIONS, reproduction,
                                                mutation_probability, leaf_inner_swap_probabilty, crossover_probability, succession)

                                accuracy, std_dev, min_score, max_score = cross_validate(
                                    model, data[0], data[1]
                                )

                                with open(f'./experiment_results/{name}.csv', 'a+') as file:
                                    file.write(
                                        f"{seed_nr},{max_depth},{j},{mutation_probability},{leaf_inner_swap_probabilty},"
                                        f"{crossover_probability},{k},{accuracy},{std_dev},{min_score},{max_score}\n"
                                    )

if __name__ == "__main__":
    datasets = prepare_datasets()

    counters = dict([(name, 0) for name in datasets])
    file_lengths = dict([(name, 0) for name in datasets])
    for name in datasets:
        try:
            file = open(f'./experiment_results/{name}.csv', 'r+')
            file_lengths[name] = sum([1 for _ in file])
            file.close()
        except Exception:
            file_lengths[name] = 0

    processes = []

    for name, data in datasets.items():
        process = Process(target=run_experiment, args=(name, data, counters, file_lengths))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

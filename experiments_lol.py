import pandas as pd
from sklearn.model_selection import train_test_split
from helpers import RANDOM_STATE, cross_validate
from evo_tree import EvoTree
from reproduction import *
from succesion import *
from random import seed

pop_size = 20
max_iters = 500


def leaf_probability(depth): return 1 - (0.5 ** depth)


reproductions = [
    proportional_reproduction,
    lambda population, fitnesses: rank_reproduction(
        population, fitnesses, 0.05, get_k_from_a(0.05, pop_size)),
    lambda population, fitnesses: truncation_reproduction(
        population, fitnesses, 0.8),
    lambda population, fitnesses: tournament_reproduction(
        population, fitnesses, 2),
]

succesions = [
    generational_succession,
    lambda population, genetic_operations_population, scores, genetic_operations_scores: elite_succession(
        population, genetic_operations_population, scores, genetic_operations_scores, 2),
]

data = pd.read_csv('./datasets/high_diamond_ranked_10min.csv')

target = data['blueWins']

attrs = data.drop(columns=['gameId', 'blueWins'])

x, x_test, y, y_test = train_test_split(
    attrs, target, test_size=0.2, random_state=RANDOM_STATE)

counter = 0
try:
    file = open('./experiment_results/breast_lol.csv', 'r+')
    file_length = sum([1 for _ in file])
    file.close()
except Exception:
    file_length = 0

for seed_nr in range(13):
    for max_depth in [5, 20]:
        for j, reproduction in enumerate(reproductions):
            for mutation_probability in [0.4, 0.8]:
                for leaf_inner_swap_probabilty in [0, 0.3]:
                    for crossover_probability in [0, 0.4]:
                        for k, succesion in enumerate(succesions):

                            counter += 1

                            if counter <= file_length:
                                continue

                            seed(seed_nr)

                            model = EvoTree(pop_size, max_depth, leaf_probability, max_iters, reproduction,
                                            mutation_probability, leaf_inner_swap_probabilty, crossover_probability, succesion)

                            accuracy, std_dev, min_score, max_score = cross_validate(
                                model, x, y)

                            file = open(
                                './experiment_results/lol.csv', "a+")
                            file.write(
                                f"{seed_nr},{max_depth},{j},{mutation_probability},{leaf_inner_swap_probabilty},{crossover_probability},{k},{accuracy},{std_dev},{min_score},{max_score}\n"
                            )
                            file.close()

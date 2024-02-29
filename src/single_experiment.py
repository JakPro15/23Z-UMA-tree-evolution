# Authors: Paweł Kochański, Jakub Proboszcz
# Written as a part of project in course UMA in semester 23Z

from evo_tree import EvoTree
from random import seed
from experiments_evotree import POPULATION_SIZE, MAX_ITERATIONS, leaf_probability
from helpers import cross_validate, RANDOM_STATE
from reproduction import *
from succession import *
from helpers import extract_data_uciml
import pandas as pd
from sklearn.model_selection import train_test_split
from ucimlrepo import fetch_ucirepo
import statistics
from aggregate_results import get_std_dev
import numpy as np


# Executes a single experiment of the tree evolution algorithm for hyperparameters
# set directly in the code.


def load_lol_dataset():
    data = pd.read_csv('./datasets/high_diamond_ranked_10min.csv')
    target = data['blueWins']
    attrs = data.drop(columns=['gameId', 'blueWins'])
    x, x_test, y, y_test = train_test_split(
        attrs, target, test_size=0.2, random_state=RANDOM_STATE)
    return (x, y, x_test, y_test)


if __name__ == "__main__":
    # reproduction and succession given as strings, so they can be printed
    parameters = dict(
        dataset_name="wine",
        max_depth=5,
        reproduction="lambda p, o: rank_reproduction(p, o, 0.01, get_k_from_a(0.01, 20))",
        mutation_probability=0.4,
        leaf_inner_swap_probabilty=0.9,
        crossover_probability=0.0,
        succession="lambda p1, p2, o1, o2: elite_succession(p1, p2, o1, o2, 2)"
    )
    for key, value in parameters.items():
        print(f"{key}: {value}")

    if parameters["dataset_name"] == "breast_cancer":
        data = extract_data_uciml(fetch_ucirepo(id=17).data)
    elif parameters["dataset_name"] == "dry_bean":
        data = extract_data_uciml(fetch_ucirepo(id=602).data)
    elif parameters["dataset_name"] == "glass":
        data = extract_data_uciml(fetch_ucirepo(id=42).data)
    elif parameters["dataset_name"] == "wine":
        data = extract_data_uciml(fetch_ucirepo(id=109).data)
    elif parameters["dataset_name"] == "lol":
        data = load_lol_dataset()
    else:
        raise ValueError("Unknown dataset")

    parameters["reproduction"] = eval(parameters["reproduction"])
    parameters["succession"] = eval(parameters["succession"])
    del parameters["dataset_name"]

    accuracies = []
    std_devs = []
    min_scores = []
    max_scores = []
    for i, seed_nr in enumerate([0, 1, 3, 5, 6]):
        seed(seed_nr)

        model = EvoTree(
            pop_size=POPULATION_SIZE,
            leaf_probability=leaf_probability,
            iter_max=MAX_ITERATIONS,
            **parameters
        )

        accuracy, std_dev, min_score, max_score = cross_validate(
            model, data[0], data[1]
        )
        accuracies.append(accuracy)
        std_devs.append(std_dev)
        min_scores.append(min_score)
        max_scores.append(max_score)
        print(f"\r{i + 1}/5 done")

    accuracy = statistics.mean(accuracies)
    std_dev = get_std_dev(accuracy, np.sum(np.array(accuracies) ** 2), np.sum(np.array(std_devs) ** 2))
    min_score = min(min_scores)
    max_score = max(max_scores)
    print(f"{accuracy=},{std_dev=},{min_score=},{max_score=}")

import os
import pickle

checkpoint_file = "checkpoint.pkl"

from helpers import prepare_datasets
from random import seed
from reproduction import tournament_reproduction
from succession import elite_succession
from sklearn.metrics import accuracy_score, confusion_matrix, ConfusionMatrixDisplay
from statistics import mean, stdev
import matplotlib.pyplot as plt
import pandas as pd
import six
import sys
sys.modules['sklearn.externals.six'] = six
import numpy as np
np.float = float
from id3 import Id3Estimator
from evo_tree import EvoTree

def fit_predict_save(model: EvoTree | Id3Estimator, datasets: dict[str, tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series]],
                     results: dict[str, list[list, list, None | list]],
                     name: str, official_name: str):
    model.fit(datasets[name][0], datasets[name][1])

    prediction = model.predict(datasets[name][2])

    results[official_name][0].append(accuracy_score(datasets[name][3], prediction))
    results[official_name][1].append(confusion_matrix(datasets[name][3], prediction))
    if results[official_name][2] is None:
        results[official_name][2] = list(model.map_dict.keys())

def save_results(results: dict[str, list[list, list, None | list]], algorithm_type: str):
    with open(f"tables_{algorithm_type}.txt", "w+") as file:
        headers = ["Nazwa zbioru danych", "średnia dokładność", "odchylenie standardowe", "dokładność minimalna", "dokładność maksymalna"]
        file.write(" ".join(["-" * len(header) for header in headers]) + "\n")
        file.write("Nazwa zbioru danych średnia dokładność odchylenie standardowe dokładność minimalna dokładność maksymalna\n")

        for name, result in results.items():
            accuracy = mean(result[0])
            std_dev = stdev(result[0])
            min_val = min(result[0])
            max_val = max(result[0])

            with open(f"tables_{algorithm_type}.txt", "a+") as file:
                file.write(f"|{name}|{accuracy:.2f}|{std_dev:.2f}|{min_val:.2f}|{max_val:.2f}|")

            confusion = np.add.reduce(result[1]) / len(result[1])
            ConfusionMatrixDisplay(result[1], display_labels=result[2]).plot()
            plt.title(f"Macierz pomyłek dla zbioru {name}\ndla algorytmu {algorithm_type}")
            plt.savefig(f"confusion_{algorithm_type}_{name}.png")


if __name__ == "__main__":

    datasets = prepare_datasets()

    def leaf_probability(depth): return 1 - (0.5 ** depth)

    pop_size = 20
    max_iters = 500
    reproduction = lambda population, fitnesses: tournament_reproduction(population, fitnesses, 2)
    succession = lambda population, genetic_operations_population, scores, genetic_operations_scores: elite_succession(
        population, genetic_operations_population, scores, genetic_operations_scores, 2)

    results_evo = {
        "breast_cancer_wisconsin_diagnostic": [[], [], None],
        "dry_bean_dataset": [[], [], None],
        "glass_identification": [[], [], None],
        "high_diamond_ranked_10min": [[], [], None],
        "wine": [[], [], None],
    }
    results_id3 = {
        "breast_cancer_wisconsin_diagnostic": [[], [], None],
        "dry_bean_dataset": [[], [], None],
        "glass_identification": [[], [], None],
        "high_diamond_ranked_10min": [[], [], None],
        "wine": [[], [], None],
    }

    if os.path.exists(checkpoint_file):
        print("Resuming from the checkpoint.")
        with open(checkpoint_file, "rb") as checkpoint_fp:
            checkpoint_data = pickle.load(checkpoint_fp)
        start_seed = checkpoint_data["seed_nr"] + 1  # Continue from the next seed
        results_evo = checkpoint_data["results_evo"]
        results_id3 = checkpoint_data["results_id3"]
    else:
        start_seed = 0

    for seed_nr in range(start_seed, 50):
        try:
            seed(seed_nr)
            np.random.seed(seed_nr)

            model = EvoTree(pop_size, 5, leaf_probability, max_iters, reproduction, 0.8, 0.3, 0.4, succession)
            fit_predict_save(model, datasets, results_evo, "breast_cancer", "breast_cancer_wisconsin_diagnostic")

            model = EvoTree(pop_size, 5, leaf_probability, max_iters, reproduction, 0.8, 0.3, 0.0, succession)
            fit_predict_save(model, datasets, results_evo, "dry_bean", "dry_bean_dataset")

            model = EvoTree(pop_size, 5, leaf_probability, max_iters, reproduction, 0.8, 0.3, 0.0, succession)
            fit_predict_save(model, datasets, results_evo, "glass", "glass_identification")

            model = EvoTree(pop_size, 5, leaf_probability, max_iters, reproduction, 0.8, 0.3, 0.4, succession)
            fit_predict_save(model, datasets, results_evo, "lol", "high_diamond_ranked_10min")

            model = EvoTree(pop_size, 5, leaf_probability, max_iters, reproduction, 0.4, 0.0, 0.4, succession)
            fit_predict_save(model, datasets, results_evo, "wine", "wine")

            model = Id3Estimator(5, 1, False, False, 0.0, True)
            fit_predict_save(model, datasets, results_id3, "breast_cancer", "breast_cancer_wisconsin_diagnostic")

            model = Id3Estimator(20, 10, True, True, 0.0, True)
            fit_predict_save(model, datasets, results_id3, "dry_bean", "dry_bean_dataset")

            model = Id3Estimator(20, 1, False, False, 0.0, True)
            fit_predict_save(model, datasets, results_id3, "glass", "glass_identification")

            model = Id3Estimator(5, 10, False, True, 0.0, True)
            fit_predict_save(model, datasets, results_id3, "lol", "high_diamond_ranked_10min")

            model = Id3Estimator(5, 1, True, False, 0.0, True)
            fit_predict_save(model, datasets, results_id3, "wine", "wine")

            checkpoint_data = {
                "seed_nr": seed_nr,
                "results_evo": results_evo,
                "results_id3": results_id3,
            }
        except KeyboardInterrupt:
            print("Execution interrupted. Saving checkpoint.")
            with open(checkpoint_file, "wb") as checkpoint_fp:
                pickle.dump(checkpoint_data, checkpoint_fp)
            raise KeyboardInterrupt

    save_results(results_evo, "ewolucja drzew")
    save_results(results_id3, "id3")
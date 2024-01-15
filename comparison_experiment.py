# Authors: Paweł Kochański, Jakub Proboszcz
# Written as a part of project in course UMA in semester 23z

from helpers import prepare_datasets
from random import seed
from reproduction import tournament_reproduction
from succession import elite_succession
from sklearn.metrics import accuracy_score, confusion_matrix, ConfusionMatrixDisplay
from statistics import mean, stdev
import matplotlib.pyplot as plt
import pandas as pd
import multiprocessing
import six
import sys
sys.modules['sklearn.externals.six'] = six
import numpy as np
np.float = float
# necessary for id3 library to function
from id3 import Id3Estimator
from evo_tree import EvoTree



# Script executes comparison of tree evolution and ID3 algorithms with their best hyperparameter values,
# on training and testing sets.


def fit_predict_save(model: EvoTree | Id3Estimator, datasets: dict[str, tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series]],
                     results_test: dict[str, list[list, list, None | np.ndarray]],
                     results_train: dict[str, list[list, list, None | np.ndarray]],
                     name: str, official_name: str):

    model.fit(datasets[name][0], datasets[name][1])

    prediction_test = model.predict(datasets[name][2])
    results_test[official_name][0].append(accuracy_score(datasets[name][3], prediction_test))
    results_test[official_name][1].append(confusion_matrix(datasets[name][3], prediction_test))

    prediction_train = model.predict(datasets[name][0])
    results_train[official_name][0].append(accuracy_score(datasets[name][1], prediction_train))
    results_train[official_name][1].append(confusion_matrix(datasets[name][1], prediction_train))

    if results_test[official_name][2] is None:
        if(isinstance(model, Id3Estimator)):
            results_test[official_name][2] = model.y_encoder.classes_
            results_train[official_name][2] = model.y_encoder.classes_

def save_results(results: dict[str, list[list, list, None | np.ndarray]], algorithm_type: str, type: str):
    longest_results_name_length = len(max(list(results), key=lambda x: len(x)))
    with open(f"results/tables_{type}_{algorithm_type}.txt", "w+") as file:
        headers = ["Nazwa zbioru danych", "średnia dokładność", "odchylenie standardowe", "dokładność minimalna", "dokładność maksymalna"]
        file.write(f"{'Nazwa zbioru danych': ^{longest_results_name_length}} średnia dokładność odchylenie standardowe dokładność minimalna dokładność maksymalna\n")
        file.write("-" * (longest_results_name_length - len(headers[0])) + " ".join(["-" * len(header) for header in headers]) + "\n")

    for name, result in results.items():
        accuracy = mean(result[0])
        std_dev = stdev(result[0])
        min_val = min(result[0])
        max_val = max(result[0])

        with open(f"results/tables_{type}_{algorithm_type}.txt", "a+") as file:
            file.write(
                f"{name: ^{longest_results_name_length}} {accuracy: ^{len(headers[1])}.2f} "
                f"{std_dev: ^{len(headers[2])}.2f} {min_val: ^{len(headers[3])}.2f} "
                f"{max_val: ^{len(headers[4])}.2f}\n"
        )

        result[1] = np.add.reduce(result[1]) / len(result[1])
        plt.rcParams.update({'font.size': 7})
        ConfusionMatrixDisplay(result[1], display_labels=result[2]).plot(values_format='.2f')
        plt.title(f"Macierz pomyłek dla zbioru {name}\ndla algorytmu {algorithm_type} dla zbioru {'testowego' if type == 'test' else 'treningowego'}")
        plt.savefig(f"plots/confusion_{type}_{algorithm_type}_{name}.png")


if __name__ == "__main__":

    datasets = prepare_datasets()

    def leaf_probability(depth): return 1 - (0.5 ** depth)

    pop_size = 20
    max_iters = 500
    reproduction = lambda population, fitnesses: tournament_reproduction(population, fitnesses, 2)
    succession = lambda population, genetic_operations_population, scores, genetic_operations_scores: elite_succession(
        population, genetic_operations_population, scores, genetic_operations_scores, 2)

    def do_loop(seed_start: int, seed_end: int,
                results_evo_test: dict[str, list[list, list, None | np.ndarray]],
                results_id3_test: dict[str, list[list, list, None | np.ndarray]],
                results_evo_train: dict[str, list[list, list, None | np.ndarray]],
                results_id3_train: dict[str, list[list, list, None | np.ndarray]]
                ) -> None:
        for seed_nr in range(seed_start, seed_end):
            seed(seed_nr)
            np.random.seed(seed_nr)

            model = EvoTree(pop_size, 5, leaf_probability, max_iters, reproduction, 0.8, 0.3, 0.4, succession)
            fit_predict_save(model, datasets, results_evo_test, results_evo_train, "breast_cancer", "breast_cancer_wisconsin_diagnostic")

            model = EvoTree(pop_size, 5, leaf_probability, max_iters, reproduction, 0.8, 0.3, 0.0, succession)
            fit_predict_save(model, datasets, results_evo_test, results_evo_train, "dry_bean", "dry_bean_dataset")

            model = EvoTree(pop_size, 5, leaf_probability, max_iters, reproduction, 0.8, 0.3, 0.0, succession)
            fit_predict_save(model, datasets, results_evo_test, results_evo_train, "glass", "glass_identification")

            model = EvoTree(pop_size, 5, leaf_probability, max_iters, reproduction, 0.8, 0.3, 0.4, succession)
            fit_predict_save(model, datasets, results_evo_test, results_evo_train, "lol", "high_diamond_ranked_10min")

            model = EvoTree(pop_size, 5, leaf_probability, max_iters, reproduction, 0.4, 0.0, 0.4, succession)
            fit_predict_save(model, datasets, results_evo_test, results_evo_train, "wine", "wine")

            model = Id3Estimator(5, 1, False, False, 0.0, True)
            fit_predict_save(model, datasets, results_id3_test, results_id3_train, "breast_cancer", "breast_cancer_wisconsin_diagnostic")

            model = Id3Estimator(20, 10, True, True, 0.0, True)
            fit_predict_save(model, datasets, results_id3_test, results_id3_train, "dry_bean", "dry_bean_dataset")

            model = Id3Estimator(20, 1, False, False, 0.0, True)
            fit_predict_save(model, datasets, results_id3_test, results_id3_train, "glass", "glass_identification")

            model = Id3Estimator(5, 10, False, True, 0.0, True)
            fit_predict_save(model, datasets, results_id3_test, results_id3_train, "lol", "high_diamond_ranked_10min")

            model = Id3Estimator(5, 1, True, False, 0.0, True)
            fit_predict_save(model, datasets, results_id3_test, results_id3_train, "wine", "wine")

            print(f"Finished seed {seed_nr}")

    def get_base_results_dict(manager: multiprocessing.Manager) -> dict[str, list[list, list, None | np.ndarray]]:
        """
        The dict contains, for each dataset:
        - list of resulting accuracies for each of the 50 algorithm executions
        - list of resulting confusion matrices for each of the 50 algorithm executions
        - numpy.ndarray of class labels for confusion matrix display
        wrapped in multiprocessing.Manager structures, for safe parallelism.
        """
        return manager.dict({
            "breast_cancer_wisconsin_diagnostic": manager.list([manager.list(), manager.list(), None]),
            "dry_bean_dataset": manager.list([manager.list(), manager.list(), None]),
            "glass_identification": manager.list([manager.list(), manager.list(), None]),
            "high_diamond_ranked_10min": manager.list([manager.list(), manager.list(), None]),
            "wine": manager.list([manager.list(), manager.list(), None]),
        })

    def change_results_dict_to_regular_form(results_evo, results_id3):
        results_evo = dict(results_evo)
        for key in results_evo:
            results_evo[key] = list(results_evo[key])
            results_evo[key][0] = list(results_evo[key][0])
            results_evo[key][1] = list(results_evo[key][1])

        results_id3 = dict(results_id3)
        for key in results_id3:
            results_id3[key] = list(results_id3[key])
            results_id3[key][0] = list(results_id3[key][0])
            results_id3[key][1] = list(results_id3[key][1])

        for key in results_evo:
            results_evo[key][2] = results_id3[key][2]

        return results_evo, results_id3

    manager = multiprocessing.Manager()
    results_evo_test = get_base_results_dict(manager)
    results_id3_test = get_base_results_dict(manager)
    results_evo_train = get_base_results_dict(manager)
    results_id3_train = get_base_results_dict(manager)

    with multiprocessing.Pool(processes=5) as pool:
        pool.starmap(do_loop, [(10 * seed_nr, 10 * (seed_nr + 1), results_evo_test, results_id3_test,
                                results_evo_train, results_id3_train) for seed_nr in range(5)])

    results_evo_test, results_id3_test = change_results_dict_to_regular_form(results_evo_test, results_id3_test)
    results_evo_train, results_id3_train = change_results_dict_to_regular_form(results_evo_train, results_id3_train)

    save_results(results_evo_test, "ewolucja drzew", "test")
    save_results(results_id3_test, "id3", "test")
    save_results(results_evo_train, "ewolucja drzew", "train")
    save_results(results_id3_train, "id3", "train")
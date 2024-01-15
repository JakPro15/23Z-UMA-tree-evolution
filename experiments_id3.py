# Authors: Paweł Kochański, Jakub Proboszcz
# Written as a part of project in course UMA in semester 23z

import six
import sys
import numpy as np
# necessary for id3 library to function
sys.modules['sklearn.externals.six'] = six
np.float = float
from id3 import Id3Estimator
from helpers import cross_validate, prepare_datasets
from multiprocessing import Process


# Script executes hyperparameter grid search for ID3 algorithm.


def run_experiment(name, data, counters, file_lengths):
    for seed_nr in range(25):
        for max_depth in [5, 20]:
            for min_samples_split in [1, 2, 10]:
                for prune in [True, False]:
                    for gain_ratio in [True, False]:
                        for min_entropy_decrease in [0., 0.3]:
                            for repeating in [True, False]:
                                counters[name] += 1
                                if counters[name] <= file_lengths[name]:
                                    continue

                                np.random.seed(seed_nr)

                                model = Id3Estimator(
                                    max_depth, min_samples_split, prune, gain_ratio, min_entropy_decrease, repeating)

                                accuracy, std_dev, min_score, max_score = cross_validate(
                                    model, data[0], data[1])

                                with open(f'./experiment_results/id3_{name}.csv', 'a+') as file:
                                    file.write(
                                        f"{seed_nr},{max_depth},{min_samples_split},{prune},{gain_ratio},{min_entropy_decrease},"
                                        f"{repeating},{accuracy},{std_dev},{min_score},{max_score}\n")

if __name__ == "__main__":
    datasets = prepare_datasets()

    counters = dict([(name, 0) for name in datasets])
    file_lengths = dict([(name, 0) for name in datasets])
    for name in datasets:
        try:
            file = open(f'./experiment_results/id3_{name}.csv', 'r+')
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

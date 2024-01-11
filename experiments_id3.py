from ucimlrepo import fetch_ucirepo
from sklearn.model_selection import train_test_split
import pandas as pd
import six
import sys
sys.modules['sklearn.externals.six'] = six
import numpy as np
np.float = float
from id3 import Id3Estimator
from helpers import cross_validate, RANDOM_STATE
from multiprocessing import Process


def extract_data_uciml(data):
    target = data.targets.squeeze()
    attrs = data.features

    x, _, y, _ = train_test_split(
        attrs, target, test_size=0.2, random_state=RANDOM_STATE)

    return (x, y)

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
                                        f"{seed_nr},{max_depth},{min_samples_split},{prune},{gain_ratio},{min_entropy_decrease},{repeating},{accuracy},{std_dev},{min_score},{max_score}\n")

if __name__ == "__main__":
    datasets = {}

    datasets["breast_cancer"] = extract_data_uciml(fetch_ucirepo(id=17).data)
    datasets["dry_bean"] = extract_data_uciml(fetch_ucirepo(id=602).data)
    datasets["glass"] = extract_data_uciml(fetch_ucirepo(id=42).data)
    datasets["wine"] = extract_data_uciml(fetch_ucirepo(id=109).data)

    data = pd.read_csv('./datasets/high_diamond_ranked_10min.csv')

    target = data['blueWins']

    attrs = data.drop(columns=['gameId', 'blueWins'])

    x, _, y, _ = train_test_split(
        attrs, target, test_size=0.2, random_state=RANDOM_STATE)

    datasets["lol"] = (x, y)

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

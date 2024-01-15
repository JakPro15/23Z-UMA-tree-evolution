# Authors: Paweł Kochański, Jakub Proboszcz
# Written as a part of project in course UMA in semester 23z

from aggregate_results import get_std_dev
import numpy as np
from statistics import stdev, mean
from pytest import approx


def test_get_std_dev():
    populations = [np.random.normal(size=5) for _ in range(25)]

    st_devs = [stdev(pop) for pop in populations]
    averages = [mean(pop) for pop in populations]
    averages_squared = [avg ** 2 for avg in averages]
    st_squared = [std ** 2 for std in st_devs]

    average = mean(averages)
    sum_avg_sq = sum(averages_squared)
    sum_st_sq = sum(st_squared)

    aggregated_population = np.concatenate(tuple(populations))

    assert get_std_dev(average, sum_avg_sq, sum_st_sq) == approx(stdev(
        aggregated_population))

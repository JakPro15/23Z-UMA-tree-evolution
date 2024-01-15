# Authors: Paweł Kochański, Jakub Proboszcz
# Written as a part of project in course UMA in semester 23z

from tree import DecisionTree
from random import choices
from math import floor


def proportional_reproduction(population: list[DecisionTree], fitnesses: list[float]) -> list[DecisionTree]:
    """
    Fitness values should be maximized and nonnegative.
    Trees are not copied; resulting list may contain the same trees as in original list.
    """
    return choices(population, fitnesses, k=len(population))


def get_k_from_a(a: float, population_size: int) -> float:
    return (2 - 2 * a * population_size) / (population_size - 1)


def rank_reproduction(population: list[DecisionTree], fitnesses: list[float], a: float, k: float) -> list[DecisionTree]:
    """
    Fitness values should be maximized.
    Trees are not copied; resulting list may contain the same trees as in original list.
    """
    sorted_indices = sorted(range(len(population)),
                            key=lambda i: fitnesses[i], reverse=True)
    sorted_population = [population[i] for i in sorted_indices]
    weights = [a + k * (1 - rank / len(population))
               for rank in range(len(population))]
    return choices(sorted_population, weights, k=len(population))


def truncation_reproduction(population: list[DecisionTree], fitnesses: list[float], rho: float) -> list[DecisionTree]:
    """
    Fitness values should be maximized.
    Trees are not copied; resulting list may contain the same trees as in original list.
    """
    sorted_indices = sorted(range(len(population)),
                            key=lambda i: fitnesses[i], reverse=True)
    truncated_population = [population[i]
                            for i in sorted_indices[:floor(rho * len(population)) + 1]]
    return choices(truncated_population, k=len(population))


def tournament_reproduction(population: list[DecisionTree], fitnesses: list[float], tournament_size: int) -> list[DecisionTree]:
    """
    Fitness values should be maximized.
    Trees are not copied; resulting list may contain the same trees as in original list.
    """
    tournament = [None] * tournament_size
    trees_with_fitness = list(zip(population, fitnesses))
    result: list[DecisionTree] = []
    for _ in range(len(population)):
        tournament = choices(trees_with_fitness, k=tournament_size)
        result.append(max(tournament, key=lambda tree: tree[1])[0])
    return result

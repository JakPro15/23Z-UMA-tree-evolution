# Authors: Paweł Kochański, Jakub Proboszcz
# Written as a part of project in course UMA in semester 23zs

from tree import DecisionTree


def generational_succession(population: list[DecisionTree], genetic_operations_population: list[DecisionTree],
                            scores: list[float], genetic_operations_scores: list[float]) -> tuple[list[DecisionTree], list[float]]:
    return genetic_operations_population, genetic_operations_scores


def elite_succession(population: list[DecisionTree], genetic_operations_population: list[DecisionTree],
                     scores: list[float], genetic_operations_scores: list[float],
                     elite_size: int) -> tuple[list[DecisionTree], list[float]]:

    assert elite_size < len(population)

    pop_scores = zip(population, scores)
    genetic_operations_pop_scores = zip(genetic_operations_population,
                                        genetic_operations_scores)

    pop_scores = sorted(pop_scores, key=lambda x: x[1], reverse=True)
    genetic_operations_pop_scores = sorted(
        genetic_operations_pop_scores, key=lambda x: x[1], reverse=True)

    elite_pop_scores = pop_scores[:elite_size] + \
        genetic_operations_pop_scores[:len(
            population) - elite_size]

    elite_population, elite_scores = zip(*elite_pop_scores)

    return list(elite_population), list(elite_scores)

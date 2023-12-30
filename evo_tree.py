from tree import init_tree, DecisionTree, print_tree
from typing import Callable, Any, Union
from genetic_operations import do_mutation, do_crossover
import pandas as pd
from sklearn.metrics import accuracy_score


def _accuracy(x: pd.DataFrame, y: pd.Series, tree: DecisionTree) -> float:
    predictions = [tree.predict(tuple(row[1:]))  # type: ignore
                   for row in x.itertuples()]  # type: ignore

    return float(accuracy_score(y, predictions))


class TreeNotConstructedYetException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class EvoTree:
    def __init__(self, pop_size: int, max_depth: int, leaf_probability: Callable[[int], float], iter_max: int,
                 reproduction: Callable[[list[DecisionTree], list[float]], list[DecisionTree]],
                 mutation_probability: float, leaf_inner_swap_probabilty: float,
                 crossover_probability: float,
                 succesion: Callable[[list[DecisionTree], list[DecisionTree], list[float], list[float]], tuple[list[DecisionTree], list[float]]],
                 ) -> None:
        self.pop_size = pop_size
        self.max_depth = max_depth
        self.leaf_probability = leaf_probability
        self.iter_max = iter_max
        self.reproduction = reproduction
        self.mutation_probability = mutation_probability
        self.leaf_inner_swap_probabilty = leaf_inner_swap_probabilty
        self.crossover_probability = crossover_probability
        self.succesion = succesion
        self.population = None
        self.no_attributes: int = 0
        self.domains: list[tuple[float, float]] = []
        self.no_classes: int = 0
        self.map_dict: dict[Any, int] = {}
        self.unmap_dict: dict[int, Any] = {}
        self.tree: Union[DecisionTree, None] = None

    def _init_population(self) -> list[DecisionTree]:
        return [
            init_tree(self.max_depth, self.no_attributes,
                      self.domains, self.no_classes, self.leaf_probability) for _ in range(self.pop_size)
        ]

    def _map_target(self, y: pd.Series) -> pd.Series:
        for i, value in enumerate(y.unique()):  # type: ignore
            self.map_dict[value] = i
            self.unmap_dict[i] = value

        return y.map(self.map_dict)  # type: ignore

    def fit(self, x: pd.DataFrame, y: pd.Series) -> list[float]:

        y_mapped = self._map_target(y)

        iter = 0
        self.no_attributes = len(x.columns)
        self.domains = [(x[attr].min(), x[attr].max())  # type: ignore
                        for attr in x.columns]
        self.no_classes = y_mapped.nunique()
        candidate_scores = []

        population = self._init_population()
        scores = [_accuracy(x, y_mapped, tree) for tree in population]

        best_score = max(scores)
        best_tree = population[scores.index(best_score)]

        candidate_scores.append(best_score)
        prev_score = best_score

        while (iter < self.iter_max):
            reproduction_population = self.reproduction(
                population, scores)

            genetic_operations_population = do_crossover(
                do_mutation(
                    reproduction_population, self.no_attributes, self.domains,
                    self.no_classes, self.mutation_probability,
                    self.leaf_inner_swap_probabilty, self.max_depth
                ),
                self.crossover_probability, self.max_depth)

            genetic_operations_scores = [
                _accuracy(x, y_mapped, tree) for tree in genetic_operations_population]

            candidate_score = max(genetic_operations_scores)
            candidate_tree = genetic_operations_population[genetic_operations_scores.index(
                candidate_score)]

            candidate_scores.append(candidate_score)

            if candidate_score > best_score:
                best_score = candidate_score
                best_tree = candidate_tree

            population, scores = self.succesion(
                population, genetic_operations_population, scores, genetic_operations_scores)

            iter += 1

            if iter % 50 == 0:
                if best_score == prev_score:
                    break
                else:
                    prev_score = best_score

        self.tree = best_tree
        return candidate_scores

    def predict(self, x: pd.DataFrame) -> pd.Series:
        if (self.tree is None):
            raise TreeNotConstructedYetException()
        predictions = [self.tree.predict(tuple(row[1:]))  # type: ignore
                       for row in x.itertuples()]  # type: ignore

        return pd.Series([self.unmap_dict[prediction] for prediction in predictions])

    def print_tree(self) -> None:
        if (self.tree is None):
            raise TreeNotConstructedYetException()
        print_tree(self.tree)

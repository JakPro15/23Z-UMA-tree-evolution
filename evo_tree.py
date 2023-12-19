from typing import Callable, Iterable, Any


class Node:
    def __init__(self, max_tree_height: int, attributes: set[Any], classes: set[Any], leaf_prob: float, depth: int = 0) -> None:
        pass


class EvoTree:
    def __init__(self, target_fun: Callable[[Node], float], pop_size: int, max_tree_height: int, leaf_prob: float) -> None:
        self.tree = None
        self.attributes = None
        self.classes = None
        self.target_fun = target_fun
        self.pop_size = pop_size
        self.max_tree_height = max_tree_height
        self.leaf_prob = leaf_prob

    @staticmethod
    def _init_tree(max_tree_height: int, attributes: set[Any], classes: set[Any], leaf_prob: float):
        return Node(max_tree_height, attributes, classes, leaf_prob, depth)

    def _init_population(self):
        population: list[Node] = []
        for _ in range(self.pop_size):
            population.append(EvoTree._init_tree(
                self.max_tree_height, self.attributes, self.classes, self.leaf_prob))

    def fit(self, x: Iterable[Any], y: Iterable[Any]):
        i = 0
        population = self._init_population()

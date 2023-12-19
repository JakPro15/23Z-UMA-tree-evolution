from __future__ import annotations
from typing import Callable, Iterable, Any
from abc import ABC, abstractmethod
from random import random, randint, choice, uniform


class Node(ABC):
    @abstractmethod
    def predict(self, x: tuple) -> int:
        ...


class InnerNode(Node):
    def __init__(self, attribute: int, threshold: float, children: tuple[Node, Node]) -> None:
        self.attribute = attribute
        self.threshold = threshold
        self.children = children

    def predict(self, x: tuple[float]) -> Any:
        if x[self.attribute] < self.threshold:
            return self.children[0].predict(x)
        else:
            return self.children[1].predict(x)


class LeafNode(Node):
    def __init__(self, leaf_class: int) -> None:
        self.leaf_class = leaf_class

    def predict(self, x: tuple[float]) -> Any:
        return self.leaf_class


def init_node(max_depth: int, no_attributes: int, domains: list[tuple[float, float]], no_classes: int, leaf_probability: Callable[[int], float], depth: int = 0) -> Node:
    if depth >= max_depth or random() < leaf_probability(depth):
        return LeafNode(leaf_class=randint(0, no_classes - 1))
    child_left = init_node(max_depth, no_attributes, no_classes, leaf_probability, depth + 1)
    child_right = init_node(max_depth, no_attributes, no_classes, leaf_probability, depth + 1)
    if isinstance(child_left, LeafNode) and isinstance(child_right, LeafNode) \
       and child_left.leaf_class == child_right.leaf_class:
        available_classes = list(range(no_classes))
        available_classes.remove(child_right.leaf_class)
        child_right.leaf_class = choice(available_classes)
    split_attribute = randint(0, no_attributes - 1)
    return InnerNode(attribute=split_attribute,
                     threshold=uniform(*domains[split_attribute]),
                     children=(child_left, child_right))

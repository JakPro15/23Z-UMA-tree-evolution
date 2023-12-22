from __future__ import annotations
from typing import Callable, Any, TypeAlias, TYPE_CHECKING
if TYPE_CHECKING:
    from _typeshed import SupportsWrite
from abc import ABC, abstractmethod
from random import random, randint, choice, uniform
from collections import deque


class Node(ABC):
    @abstractmethod
    def predict(self, x: tuple[float, ...]) -> int:
        ...


class InnerNode(Node):
    def __init__(self, attribute: int, threshold: float, children: tuple[Node, Node]) -> None:
        self.attribute = attribute
        self.threshold = threshold
        self.children = children

    def predict(self, x: tuple[float, ...]) -> Any:
        if x[self.attribute] < self.threshold:
            return self.children[0].predict(x)
        else:
            return self.children[1].predict(x)


class LeafNode(Node):
    def __init__(self, leaf_class: int) -> None:
        self.leaf_class = leaf_class

    def predict(self, x: tuple[float, ...]) -> Any:
        return self.leaf_class


def _init_node(max_depth: int, no_attributes: int, domains: list[tuple[float, float]], no_classes: int,
               leaf_probability: Callable[[int], float], depth: int = 0) -> Node:
    if depth >= max_depth or random() < leaf_probability(depth):
        return LeafNode(leaf_class=randint(0, no_classes - 1))
    child_left = _init_node(max_depth, no_attributes, domains, no_classes, leaf_probability, depth + 1)
    child_right = _init_node(max_depth, no_attributes, domains, no_classes, leaf_probability, depth + 1)
    if isinstance(child_left, LeafNode) and isinstance(child_right, LeafNode) \
       and child_left.leaf_class == child_right.leaf_class:
        available_classes = list(range(no_classes))
        available_classes.remove(child_right.leaf_class)
        child_right.leaf_class = choice(available_classes)
    split_attribute = randint(0, no_attributes - 1)
    return InnerNode(attribute=split_attribute,
                     threshold=uniform(*domains[split_attribute]),
                     children=(child_left, child_right))


DecisionTree: TypeAlias = Node


def init_tree(max_depth: int, no_attributes: int, domains: list[tuple[float, float]], no_classes: int,
              leaf_probability: Callable[[int], float]) -> DecisionTree:
    return _init_node(max_depth, no_attributes, domains, no_classes, leaf_probability, 0)


def _format_threshold(threshold: float) -> str:
    formatted = f"{threshold:.2f}"
    if formatted[-2] == '.':
        formatted += '0'
    return formatted


def _format_node(node: Node | None, length: int, attribute_length: int, threshold_length: int, class_length: int) -> str:
    result = ""
    if node is None:
        return ' ' * length
    elif isinstance(node, InnerNode):
        result = f'({node.attribute:>{attribute_length}}|{_format_threshold(node.threshold):<{threshold_length}})'
    elif isinstance(node, LeafNode):
        result = f'[{node.leaf_class:>{class_length}}]'
    return f'{result:^{length}}'


def _get_tree_properties(tree: DecisionTree) -> tuple[int, int, int, int]:
    """
    Traverses the tree and returns tree properties for printing.
    """
    max_class_length = 0
    max_attribute_length = 0
    max_threshold_length = 0
    tree_depth = 0
    nodes = deque[tuple[Node | None, int]]()
    nodes.append((tree, 0))
    while len(nodes) > 0:
        node, depth = nodes.popleft()
        if isinstance(node, InnerNode):
            nodes.append((node.children[0], depth + 1))
            nodes.append((node.children[1], depth + 1))
            attribute_length = len(str(node.attribute))
            if attribute_length > max_attribute_length:
                max_attribute_length = attribute_length
            threshold_length = len(_format_threshold(node.threshold))
            if threshold_length > max_threshold_length:
                max_threshold_length = threshold_length
        elif isinstance(node, LeafNode):
            if depth > tree_depth:
                tree_depth = depth
            class_length = len(str(node.leaf_class))
            if class_length > max_class_length:
                max_class_length = class_length
    return max_attribute_length, max_threshold_length, max_class_length, tree_depth


def _get_formatted_leaf_length(max_class_length: int, max_attribute_length: int, max_threshold_length: int) -> int:
    leaf_length = max_class_length + 2
    inner_length = max_attribute_length + max_threshold_length + 3
    while inner_length > 2 * leaf_length + 1:
        leaf_length += 1
    return leaf_length


def _format_tree_inner_layer(
    layer: int, nodes_in_layer: list[Node | None], tree_depth: int, leaf_length: int,
    max_attribute_length: int, max_threshold_length: int, max_class_length: int
) -> tuple[str, list[Node | None]]:
    result = ""
    nodes_amount = len(nodes_in_layer)
    assert nodes_amount == 2 ** layer
    leaves_per_node = 2 ** (tree_depth - layer)
    nodes_in_next_layer: list[Node | None] = []
    for i, node in enumerate(nodes_in_layer):
        result += _format_node(node, leaves_per_node * (leaf_length + 1) - 1,
                               max_attribute_length, max_threshold_length, max_class_length)
        if i < len(nodes_in_layer) - 1:
            result += ' '
        if isinstance(node, InnerNode):
            nodes_in_next_layer.append(node.children[0])
            nodes_in_next_layer.append(node.children[1])
        else:
            nodes_in_next_layer.append(None)
            nodes_in_next_layer.append(None)
    nodes_in_layer = nodes_in_next_layer
    result += '\n'
    return result, nodes_in_next_layer


def print_tree(tree: DecisionTree, file: SupportsWrite[str] | None = None) -> None:
    """
    Printed tree format is as follows:
    inner node with attribute n and threshold m: (n|m)
    threshold is printed with 2 decimal places
    leaf node with class c: [c]
    Example (from initial documentation pages 1-2; a_1 is attribute 0, a_2 is 1):
      (0|4.00)
    [1]    (1|2.00)
           [0]  [1]
    """
    max_attribute_length, max_threshold_length, max_class_length, tree_depth = _get_tree_properties(tree)
    leaf_length = _get_formatted_leaf_length(max_class_length, max_attribute_length, max_threshold_length)

    result = ""
    nodes_in_layer: list[Node | None] = [tree]
    for layer in range(tree_depth):
        formatted_layer, nodes_in_layer = _format_tree_inner_layer(
            layer, nodes_in_layer, tree_depth, leaf_length,
            max_attribute_length, max_threshold_length, max_class_length
        )
        result += formatted_layer

    for i, node in enumerate(nodes_in_layer):
        result += _format_node(node, leaf_length, max_attribute_length, max_threshold_length, max_class_length)
        if i < len(nodes_in_layer) - 1:
            result += ' '
    print(result, file=file)

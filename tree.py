from __future__ import annotations
from typing import Callable, TYPE_CHECKING, overload
from typing_extensions import Self
if TYPE_CHECKING:
    from _typeshed import SupportsWrite
from abc import ABC, abstractmethod
from random import random, randint, choice, uniform
from collections import deque
import pandas as pd
import numpy as np


class SubtreeIterator:
    def __init__(self, root: Node) -> None:
        self.iteration_queue = deque[Node]([root])

    def __iter__(self) -> Self:
        return self

    def __next__(self) -> Node:
        if len(self.iteration_queue) == 0:
            raise StopIteration
        node = self.iteration_queue.popleft()
        if isinstance(node, InnerNode):
            self.iteration_queue.append(node.children[0])
            self.iteration_queue.append(node.children[1])
        return node


class Node(ABC):
    parent: InnerNode | None

    @abstractmethod
    @overload
    def predict(self, x: tuple[float, ...]) -> int:
        ...

    @abstractmethod
    @overload
    def predict(self, x: pd.DataFrame) -> pd.Series[int]:
        ...

    @abstractmethod
    def predict(self, x: tuple[float, ...] | pd.DataFrame) -> int | pd.Series[int]:
        ...

    def subtree_nodes(self) -> SubtreeIterator:
        return SubtreeIterator(self)

    def depth(self) -> int:
        depth = 0
        parent = self.parent
        while parent is not None:
            parent = parent.parent
            depth += 1
        return depth

    @abstractmethod
    def copy(self) -> Node:
        ...


class InnerNode(Node):
    def __init__(self, attribute: int, threshold: float, children: tuple[Node, Node], parent: InnerNode | None = None) -> None:
        self.attribute = attribute
        self.threshold = threshold
        self.children = children
        self.children[0].parent = self
        self.children[1].parent = self
        self.parent = parent

    @overload
    def predict(self, x: tuple[float, ...]) -> int:
        ...

    @overload
    def predict(self, x: pd.DataFrame) -> pd.Series[int]:
        ...

    def predict(self, x: tuple[float, ...] | pd.DataFrame) -> int | pd.Series[int]:
        if isinstance(x, pd.DataFrame):
            mask = x.iloc[:, self.attribute] < self.threshold
            return pd.concat([self.children[0].predict(x[mask]), self.children[1].predict(x[~mask])]) # type: ignore
        if x[self.attribute] < self.threshold:
            return self.children[0].predict(x)
        else:
            return self.children[1].predict(x)

    def copy(self) -> InnerNode:
        return InnerNode(self.attribute, self.threshold, (self.children[0].copy(), self.children[1].copy()), self.parent)


class LeafNode(Node):
    def __init__(self, leaf_class: int, parent: InnerNode | None = None) -> None:
        self.leaf_class = leaf_class
        self.parent = parent

    @overload
    def predict(self, x: tuple[float, ...]) -> int:
        ...

    @overload
    def predict(self, x: pd.DataFrame) -> pd.Series[int]:
        ...

    def predict(self, x: tuple[float, ...] | pd.DataFrame) -> int | pd.Series[int]:
        if isinstance(x, pd.DataFrame):
            return pd.Series(self.leaf_class, index=x.index)
        return self.leaf_class

    def copy(self) -> LeafNode:
        return LeafNode(self.leaf_class, self.parent)


def init_node(max_depth: int, no_attributes: int, domains: list[tuple[float, float]], no_classes: int,
              leaf_probability: Callable[[int], float], depth: int, X_train: pd.DataFrame, y_train: pd.Series[int],
              parent: InnerNode | None = None) -> Node:
    if depth >= max_depth or random() < leaf_probability(depth):
        if len(y_train) > 0:
            return LeafNode(leaf_class=y_train.mode().iloc[0])
        else:
            return LeafNode(leaf_class=randint(0, no_classes - 1))
    split_attribute = randint(0, no_attributes - 1)
    split_threshold = uniform(*domains[split_attribute])
    if len(X_train) > 0:
        mask = X_train.iloc[:, split_attribute] < split_threshold
        child_left = init_node(max_depth, no_attributes, domains, no_classes, leaf_probability, depth + 1, X_train[mask], y_train[mask])
        child_right = init_node(max_depth, no_attributes, domains, no_classes, leaf_probability, depth + 1, X_train[~mask], y_train[~mask])
    else:
        child_left = init_node(max_depth, no_attributes, domains, no_classes, leaf_probability, depth + 1, X_train, y_train)
        child_right = init_node(max_depth, no_attributes, domains, no_classes, leaf_probability, depth + 1, X_train, y_train)
    if isinstance(child_left, LeafNode) and isinstance(child_right, LeafNode) \
       and child_left.leaf_class == child_right.leaf_class:
        available_classes = list(range(no_classes))
        available_classes.remove(child_right.leaf_class)
        child_right.leaf_class = choice(available_classes)
    created_node = InnerNode(attribute=split_attribute,
                             threshold=split_threshold,
                             children=(child_left, child_right),
                             parent=parent)
    return created_node


class DecisionTree:
    def __init__(self, root: Node) -> None:
        self.root = root

    def nodes(self) -> SubtreeIterator:
        return self.root.subtree_nodes()

    def depth(self) -> int:
        depth = 0
        for node in self.nodes():
            if isinstance(node, LeafNode):
                node_depth = node.depth()
                if node_depth > depth:
                    depth = node_depth
        return depth

    @overload
    def predict(self, x: tuple[float, ...]) -> int:
        ...

    @overload
    def predict(self, x: pd.DataFrame) -> pd.Series[int]:
        ...

    def predict(self, x: tuple[float, ...] | pd.DataFrame) -> int | pd.Series[int]:
        if isinstance(x, pd.DataFrame):
            return self.root.predict(x).reindex(x.index)
        else:
            return self.root.predict(x)

    def copy(self) -> DecisionTree:
        return DecisionTree(self.root.copy())


def init_tree(max_depth: int, no_attributes: int, domains: list[tuple[float, float]], no_classes: int,
              leaf_probability: Callable[[int], float], X_train: pd.DataFrame, y_train: pd.Series[int]) -> DecisionTree:
    return DecisionTree(init_node(max_depth, no_attributes, domains, no_classes, leaf_probability, 0, X_train, y_train))


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
        result = f'({node.attribute:>{attribute_length}}|' \
            f'{_format_threshold(node.threshold):<{threshold_length}})'
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
    for node in tree.nodes():
        if isinstance(node, InnerNode):
            attribute_length = len(str(node.attribute))
            if attribute_length > max_attribute_length:
                max_attribute_length = attribute_length
            threshold_length = len(_format_threshold(node.threshold))
            if threshold_length > max_threshold_length:
                max_threshold_length = threshold_length
        elif isinstance(node, LeafNode):
            depth = node.depth()
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
    max_attribute_length, max_threshold_length, max_class_length, tree_depth = _get_tree_properties(
        tree)
    leaf_length = _get_formatted_leaf_length(
        max_class_length, max_attribute_length, max_threshold_length)

    result = ""
    nodes_in_layer: list[Node | None] = [tree.root]
    for layer in range(tree_depth):
        formatted_layer, nodes_in_layer = _format_tree_inner_layer(
            layer, nodes_in_layer, tree_depth, leaf_length,
            max_attribute_length, max_threshold_length, max_class_length
        )
        result += formatted_layer

    for i, node in enumerate(nodes_in_layer):
        result += _format_node(node, leaf_length, max_attribute_length,
                               max_threshold_length, max_class_length)
        if i < len(nodes_in_layer) - 1:
            result += ' '
    print(result, file=file)

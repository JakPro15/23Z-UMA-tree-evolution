# Authors: Paweł Kochański, Jakub Proboszcz
# Written as a part of project in course UMA in semester 23Z

from tree import DecisionTree, Node, InnerNode, LeafNode, init_node
from typing import Union
from random import random, choice, uniform, shuffle, randint
import pandas as pd


def _replace_child(tree: DecisionTree, parent: Union[InnerNode, None], old_child: Node, new_child: Node) -> None:
    new_child.parent = parent
    if parent is not None:
        if parent.children[0] == old_child:
            parent.children = (new_child, parent.children[1])
        else:
            parent.children = (parent.children[0], new_child)
    else:
        tree.root = new_child


def _attempt_rollup(tree: DecisionTree, node: InnerNode) -> None:
    if isinstance(node.children[0], LeafNode) and isinstance(node.children[1], LeafNode) and \
            node.children[0].leaf_class == node.children[1].leaf_class:
        new_node = LeafNode(node.children[0].leaf_class, node.X_train, node.y_train)
        _replace_child(tree, node.parent, node, new_node)


def _do_no_swap_mutation(node: InnerNode, no_attributes: int, domains: list[tuple[float, float]]) -> None:
    node.attribute = choice(range(no_attributes))
    node.threshold = uniform(*domains[node.attribute])


def _do_leaf_inner_swap(tree: DecisionTree, node: Node, no_attributes: int, domains: list[tuple[float, float]],
                        max_depth: int) -> None:
    if isinstance(node, LeafNode):
        if node.depth() >= max_depth:
            return
        new_leaf1 = LeafNode(None)
        new_leaf2 = LeafNode(None)
        split_attribute = randint(0, no_attributes - 1)
        split_threshold = uniform(*domains[split_attribute])
        new_inner = InnerNode(split_attribute, split_threshold, (new_leaf1, new_leaf2))
        _replace_child(tree, node.parent, node, new_inner)
    else:
        new_node = LeafNode(None)
        _replace_child(tree, node.parent, node, new_node)
        if new_node.parent is not None:
            _attempt_rollup(tree, new_node.parent)


def mutate_tree(tree: DecisionTree, no_attributes: int, domains: list[tuple[float, float]],
                mutation_probability: float, leaf_inner_swap_probability: float, max_depth: int) -> None:
    """
    Mutation is done in-place - the given trees are modified.
    """
    if not random() < mutation_probability:
        return
    if random() < leaf_inner_swap_probability:
        mutated_node = choice(list(tree.nodes()))
        _do_leaf_inner_swap(tree, mutated_node, no_attributes, domains, max_depth)
    else:
        nodes_to_mutate = [node for node in tree.nodes() if isinstance(node, InnerNode)]
        if(len(nodes_to_mutate)) == 0:
            return
        mutated_node = choice(nodes_to_mutate)
        _do_no_swap_mutation(mutated_node, no_attributes, domains)
    tree.recalculate()


def _do_crossover_swap(child1: DecisionTree, child2: DecisionTree, swapped_root1: Node, swapped_root2: Node) -> None:
    swapped_parent1 = swapped_root1.parent
    swapped_parent2 = swapped_root2.parent

    _replace_child(child1, swapped_parent1, swapped_root1, swapped_root2)
    _replace_child(child2, swapped_parent2, swapped_root2, swapped_root1)


def _check_max_depth(parent1: DecisionTree, parent2: DecisionTree, child1: DecisionTree, child2: DecisionTree, max_depth: int) -> tuple[DecisionTree, DecisionTree]:
    if child1.depth() > max_depth:
        child1 = parent1.copy()
    if child2.depth() > max_depth:
        child2 = parent2.copy()
    return (child1, child2)


def crossover_trees(parent1: DecisionTree, parent2: DecisionTree, crossover_probability: float, max_depth: int) -> tuple[DecisionTree, DecisionTree]:
    """
    Given parents are not modified; the results are always copies of the originals.
    """
    if not random() < crossover_probability:
        return (parent1.copy(), parent2.copy())
    child1 = parent1.copy()
    child2 = parent2.copy()
    swapped_root1 = choice(list(child1.nodes()))
    swapped_root2 = choice(list(child2.nodes()))
    _do_crossover_swap(child1, child2, swapped_root1, swapped_root2)
    child1.recalculate()
    child2.recalculate()
    return _check_max_depth(parent1, parent2, child1, child2, max_depth)


def do_mutation(population: list[DecisionTree], no_attributes: int, domains: list[tuple[float, float]],
                mutation_probability: float, leaf_inner_swap_probability: float, max_depth: int) -> list[DecisionTree]:
    mutated_population = [tree.copy() for tree in population]
    for tree in mutated_population:
        mutate_tree(tree, no_attributes, domains, mutation_probability, leaf_inner_swap_probability, max_depth)
    return mutated_population


def do_crossover(population: list[DecisionTree], crossover_probability: float, max_depth: int) -> list[DecisionTree]:
    shuffled_population = population.copy()
    shuffle(shuffled_population)
    result: list[DecisionTree] = []
    for i in range(len(shuffled_population) // 2):
        crossed_over = crossover_trees(
            shuffled_population[2 * i], shuffled_population[2 * i + 1], crossover_probability, max_depth)
        result.append(crossed_over[0])
        result.append(crossed_over[1])
    if len(shuffled_population) % 2 == 1:
        result.append(shuffled_population[-1])
    return result

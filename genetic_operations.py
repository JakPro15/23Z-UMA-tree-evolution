from tree import DecisionTree, Node, InnerNode, LeafNode, init_node
from typing import Any
from random import random, choice, uniform


def _replace_child(tree: DecisionTree, old_parent: InnerNode | None, old_child: Node, new_child: Node) -> None:
    new_child.parent = old_parent
    if old_parent is not None:
        if old_parent.children[0] == old_child:
            old_parent.children = (new_child, old_parent.children[1])
        else:
            old_parent.children = (old_parent.children[0], new_child)
    else:
        tree.root = new_child


def _attempt_rollup(tree: DecisionTree, node: InnerNode) -> None:
    if isinstance(node.children[0], LeafNode) and isinstance(node.children[1], LeafNode) and node.children[0].leaf_class == node.children[1].leaf_class:
        new_node = LeafNode(node.children[0].leaf_class)
        _replace_child(tree, node.parent, node, new_node)


def _do_no_swap_mutation(tree: DecisionTree, node: Node, no_attributes: int, domains: list[tuple[float, float]], no_classes: int) -> None:
    if isinstance(node, LeafNode):
        classes = list(range(no_classes))
        classes.remove(node.leaf_class)
        node.leaf_class = choice(classes)
        if node.parent is not None:
            _attempt_rollup(tree, node.parent)
    elif isinstance(node, InnerNode):
        node.attribute = choice(range(no_attributes))
        node.threshold = uniform(*domains[node.attribute])

def _get_random_max_element_index(collection: list[Any]) -> int:
    maximum = max(collection)
    return choice([
        index
        for index, value
        in enumerate(collection)
        if value == maximum
    ])

def _do_leaf_inner_swap(tree: DecisionTree, node: Node, no_attributes: int,
                        domains: list[tuple[float, float]], no_classes: int, max_depth: int) -> None:
    if isinstance(node, LeafNode):
        if node.depth() >= max_depth:
            return
        new_node = init_node(1, no_attributes, domains, no_classes, leaf_probability=lambda _: 0, parent=node.parent)
        _replace_child(tree, node.parent, node, new_node)
    else:
        leaf_classes_count = [0 for _ in range(no_classes)]
        for subnode in node.subtree_nodes():
            if isinstance(subnode, LeafNode):
                leaf_classes_count[subnode.leaf_class] += 1
        new_node = LeafNode(_get_random_max_element_index(leaf_classes_count))
        _replace_child(tree, node.parent, node, new_node)
        if new_node.parent is not None:
            _attempt_rollup(tree, new_node.parent)


def mutate_tree(tree: DecisionTree, no_attributes: int, domains: list[tuple[float, float]], no_classes: int,
                mutation_probability: float, leaf_inner_swap_probability: float, max_depth: int) -> None:
    if not random() < mutation_probability:
        return
    mutated_node = choice(list(tree.nodes()))
    if random() < leaf_inner_swap_probability:
        _do_leaf_inner_swap(tree, mutated_node, no_attributes, domains, no_classes, max_depth)
    else:
        _do_no_swap_mutation(tree, mutated_node, no_attributes, domains, no_classes)


def crossover_trees(parent1: DecisionTree, parent2: DecisionTree, crossover_probability: float, max_depth: int) -> tuple[DecisionTree, DecisionTree]:
    if not random() < crossover_probability:
        return (parent1.copy(), parent2.copy())
    child1 = parent1.copy()
    child2 = parent2.copy()
    swapped_root1 = choice(list(child1.nodes()))
    swapped_root2 = choice(list(child2.nodes()))
    swapped_parent1 = swapped_root1.parent
    swapped_parent2 = swapped_root2.parent
    _replace_child(child1, swapped_parent1, swapped_root1, swapped_root2)
    _replace_child(child2, swapped_parent2, swapped_root2, swapped_root1)
    if isinstance(swapped_root2, LeafNode) and swapped_parent1 is not None:
        _attempt_rollup(child1, swapped_parent1)
    if isinstance(swapped_root1, LeafNode) and swapped_parent2 is not None:
        _attempt_rollup(child2, swapped_parent2)
    if child1.depth() > max_depth:
        child1 = parent1.copy()
    if child2.depth() > max_depth:
        child2 = parent2.copy()
    return (child1, child2)

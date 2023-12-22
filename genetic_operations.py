from tree import DecisionTree, Node, InnerNode, LeafNode, init_node
from random import random, choice, uniform

def _do_no_swap_mutation(node: Node, no_attributes: int, domains: list[tuple[float, float]], no_classes: int) -> None:
    if isinstance(node, LeafNode):
        classes = list(range(no_classes))
        classes.remove(node.leaf_class)
        node.leaf_class = choice(classes)
    elif isinstance(node, InnerNode):
        node.attribute = choice(range(no_attributes))
        node.threshold = uniform(*domains[node.attribute])

def _do_leaf_inner_swap(tree: DecisionTree, node: Node, no_attributes: int, domains: list[tuple[float, float]], no_classes: int) -> None:
    if isinstance(node, LeafNode):
        new_node = init_node(1, no_attributes, domains, no_classes, leaf_probability=lambda _: 0, parent=node.parent)
    else:
        leaf_classes_count = [0 for _ in range(no_classes)]
        for subnode in node.subtree_nodes():
            if isinstance(subnode, LeafNode):
                leaf_classes_count[subnode.leaf_class] += 1
        max_occurrences = max(leaf_classes_count)
        new_node = LeafNode(choice([
            leaf_class
            for leaf_class, count
            in enumerate(leaf_classes_count)
            if count == max_occurrences
        ]), node.parent)
    if node.parent is not None:
        if node.parent.children[0] == node:
            node.parent.children = (new_node, node.parent.children[1])
        else:
            node.parent.children = (node.parent.children[0], new_node)
    else:
        tree.root = new_node


def mutate_tree(tree: DecisionTree, no_attributes: int, domains: list[tuple[float, float]], no_classes: int,
                mutation_probability: float, leaf_inner_swap_probability: float) -> None:
    if not random() < mutation_probability:
        return
    mutated_node = choice(list(tree.nodes()))
    if random() < leaf_inner_swap_probability:
        _do_leaf_inner_swap(tree, mutated_node, no_attributes, domains, no_classes)
    else:
        _do_no_swap_mutation(mutated_node, no_attributes, domains, no_classes)

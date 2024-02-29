# Authors: Paweł Kochański, Jakub Proboszcz
# Written as a part of project in course UMA in semester 23Z

import genetic_operations
from tree import LeafNode, InnerNode, DecisionTree, init_tree, Node
import pandas as pd
from sklearn.datasets import make_classification
from random import seed
from collections import deque


def test_no_swap_mutation_inner_node():
    leaf1 = LeafNode(0)
    leaf2 = LeafNode(1)
    inner = InnerNode(1, 8.3, (leaf1, leaf2))
    tree = DecisionTree(inner)
    genetic_operations._do_no_swap_mutation(inner, 2, [(1, 5), (6, 10)])
    assert isinstance(tree.root, InnerNode)
    assert (tree.root.attribute == 0 and 1 <= tree.root.threshold <= 5) or \
            (tree.root.attribute == 1 and 6 <= tree.root.threshold <= 10)
    assert tree.root.parent is None


def test_swap_mutation_leaf():
    leaf = LeafNode(0)
    tree = DecisionTree(leaf)
    genetic_operations._do_leaf_inner_swap(tree, leaf, 2, [(1, 5), (6, 10)], 3)
    assert isinstance(tree.root, InnerNode)
    assert (tree.root.attribute == 0 and 1 <= tree.root.threshold <= 5) or \
           (tree.root.attribute == 1 and 6 <= tree.root.threshold <= 10)
    assert isinstance(tree.root.children[0], LeafNode)
    assert isinstance(tree.root.children[1], LeafNode)
    assert tree.root.children[0].leaf_class is None # to be assigned in upcoming recalculation
    assert tree.root.children[1].leaf_class is None
    assert tree.root.children[0].parent == tree.root
    assert tree.root.children[1].parent == tree.root
    assert tree.root.parent is None


def test_swap_mutation_leaf_max_depth():
    leaf1 = LeafNode(0)
    leaf2 = LeafNode(1)
    inner = InnerNode(1, 8.3, (leaf1, leaf2))
    tree = DecisionTree(inner)
    genetic_operations._do_leaf_inner_swap(tree, leaf1, 2, [(1, 5), (6, 10)], 1)
    assert isinstance(tree.root, InnerNode)
    assert tree.root.attribute == 1
    assert tree.root.threshold == 8.3
    assert isinstance(tree.root.children[0], LeafNode)
    assert isinstance(tree.root.children[1], LeafNode)
    assert tree.root.children[0].leaf_class == 0
    assert tree.root.children[1].leaf_class == 1
    assert tree.root.children[0].parent == tree.root
    assert tree.root.children[1].parent == tree.root
    assert tree.root.parent is None


def test_swap_mutation_inner_node():
    leaf1 = LeafNode(0)
    leaf2 = LeafNode(1)
    leaf3 = LeafNode(1)
    inner1 = InnerNode(0, 3.3, (leaf1, leaf2))
    inner2 = InnerNode(1, 8.3, (inner1, leaf3))
    tree = DecisionTree(inner2)
    genetic_operations._do_leaf_inner_swap(tree, inner2, 2, [(1, 5), (6, 10)], 3)
    assert isinstance(tree.root, LeafNode)
    assert tree.root.leaf_class is None # to be assigned in upcoming recalculation
    assert tree.root.parent is None


def test_crossover_swap():
    leaf1 = LeafNode(0)
    leaf2 = LeafNode(1)
    leaf3 = LeafNode(1)
    inner1 = InnerNode(0, 3.3, (leaf1, leaf2))
    inner2 = InnerNode(1, 8.3, (inner1, leaf3))
    tree1 = DecisionTree(inner2)

    leaf4 = LeafNode(1)
    leaf5 = LeafNode(0)
    inner3 = InnerNode(0, 2.6, (leaf4, leaf5))
    tree2 = DecisionTree(inner3)

    genetic_operations._do_crossover_swap(tree1, tree2, inner1, inner3)

    assert tree1.root == inner2
    assert isinstance(tree1.root, InnerNode)
    assert tree1.root.children == (inner3, leaf3)
    assert inner3.parent == tree1.root

    assert tree2.root == inner1
    assert isinstance(tree2.root, InnerNode)
    assert tree2.root.parent is None


def test_check_max_depth():
    seed(0)
    X_train, y_train = make_classification(200, 10, random_state=42, n_classes=10,
                                           n_informative=10, n_redundant=0, n_repeated=0)
    X_train = pd.DataFrame(X_train, index=list(range(200)), columns=list(range(10)))
    y_train = pd.Series(y_train, index=list(range(200)))
    domains = [(X_train.iloc[:, i].min(), X_train.iloc[:, i].max()) for i in range(10)]

    parent1 = init_tree(2, 10, domains, lambda _: 0, X_train, y_train)
    parent2 = init_tree(2, 10, domains, lambda _: 0, X_train, y_train)
    child1 = init_tree(4, 10, domains, lambda _: 0, X_train, y_train)
    child2 = init_tree(1, 10, domains, lambda _: 0, X_train, y_train)

    result1, result2 = genetic_operations._check_max_depth(parent1, parent2, child1, child2, 2)
    assert result1 != child1
    if isinstance(result1.root, InnerNode) and isinstance(parent1.root, InnerNode):
        assert result1.root.attribute == parent1.root.attribute
        assert result1.root.threshold == parent1.root.threshold
    elif isinstance(result1.root, LeafNode) and isinstance(parent1.root, LeafNode):
        assert result1.root.leaf_class == parent1.root.leaf_class
    else:
        raise AssertionError

    assert result2 == child2


def check_consistency(tree: DecisionTree):
    iteration_queue = deque([(tree.root, tree.X_train, tree.y_train)])
    while len(iteration_queue) != 0:
        node, X_train, y_train = iteration_queue.popleft()
        if isinstance(node, InnerNode):
            mask = X_train.iloc[:, node.attribute] < node.threshold
            iteration_queue.append((node.children[0], X_train[mask], y_train[mask]))
            iteration_queue.append((node.children[1], X_train[~mask], y_train[~mask]))
        elif isinstance(node, LeafNode):
            assert node.leaf_class in y_train.mode().values


def test_consistency():
    # Checks whether with a random dataset the tree leaf classes will be properly calculated.
    X_train, y_train = make_classification(200, 10, random_state=42)
    X_train = pd.DataFrame(X_train, index=list(range(200)), columns=list(range(10)))
    y_train = pd.Series(y_train, index=list(range(200)))
    domains = [(X_train.iloc[:, i].min(), X_train.iloc[:, i].max()) for i in range(10)]
    for _ in range(100):
        tree = init_tree(10, 5, domains, lambda _: 0.1, X_train, y_train)
        check_consistency(tree)

        tree2 = tree.copy()
        genetic_operations.mutate_tree(tree2, 10, domains, 1, 0, 10)
        check_consistency(tree2)

        tree3 = tree.copy()
        genetic_operations.mutate_tree(tree3, 10, domains, 1, 1, 10)
        check_consistency(tree3)

        tree4, tree5 = genetic_operations.crossover_trees(tree, tree3, 1, 10)
        check_consistency(tree4)
        check_consistency(tree5)

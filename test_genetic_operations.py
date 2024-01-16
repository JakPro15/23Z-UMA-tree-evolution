# Authors: Paweł Kochański, Jakub Proboszcz
# Written as a part of project in course UMA in semester 23Z

import genetic_operations
from tree import LeafNode, InnerNode, DecisionTree
import pandas as pd
from random import seed


def test_no_swap_mutation_inner_node():
    leaf1 = LeafNode(0, pd.DataFrame([(2, 7)], index=[0], columns=['a', 'b']), pd.Series([0], index=[0]))
    leaf2 = LeafNode(1, pd.DataFrame([(3, 9)], index=[0], columns=['a', 'b']), pd.Series([1], index=[0]))
    inner = InnerNode(1, 8.3, (leaf1, leaf2), pd.DataFrame([(2, 7), (3, 9)], index=[0, 1], columns=['a', 'b']),
                      pd.Series([0, 1], index=[0, 1]))
    tree = DecisionTree(inner)
    genetic_operations._do_no_swap_mutation(tree, inner, 2, [(1, 5), (6, 10)])
    if isinstance(tree.root, InnerNode):
        assert (tree.root.attribute == 0 and 1 <= tree.root.threshold <= 5) or \
               (tree.root.attribute == 1 and 6 <= tree.root.threshold <= 10)
        assert tree.root.parent is None
    else:
        assert tree.root.leaf_class in {0, 1}
        assert tree.root.X_train.equals(inner.X_train)
        assert tree.root.y_train.equals(inner.y_train)


def test_swap_mutation_leaf():
    leaf = LeafNode(0, pd.DataFrame([(2, 7), (3, 9)], index=[0, 1], columns=['a', 'b']),
                    pd.Series([0, 1], index=[0, 1]))
    tree = DecisionTree(leaf)
    genetic_operations._do_leaf_inner_swap(tree, leaf, 2, [(1, 5), (6, 10)], 3)
    if isinstance(tree.root, InnerNode):
        assert (tree.root.attribute == 0 and 1 <= tree.root.threshold <= 5) or \
               (tree.root.attribute == 1 and 6 <= tree.root.threshold <= 10)
        assert isinstance(tree.root.children[0], LeafNode)
        assert isinstance(tree.root.children[1], LeafNode)
        assert tree.root.children[0].leaf_class in {0, 1}
        assert tree.root.children[1].leaf_class in {0, 1}
        assert tree.root.children[0].leaf_class != tree.root.children[1].leaf_class
        assert tree.root.children[0].parent == tree.root
        assert tree.root.children[1].parent == tree.root
        assert tree.root.parent is None
    else:
        assert tree.root.leaf_class in {0, 1}
        assert tree.root.X_train.equals(leaf.X_train)
        assert tree.root.y_train.equals(leaf.y_train)


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
    inner2 = InnerNode(1, 8.3, (inner1, leaf3), pd.DataFrame([(2, 7), (3, 9), (1, 6)], index=[0, 1, 2], columns=['a', 'b']),
                       pd.Series([0, 1, 1], index=[0, 1, 2]))
    tree = DecisionTree(inner2)
    genetic_operations._do_leaf_inner_swap(tree, inner2, 2, [(1, 5), (6, 10)], 3)
    assert isinstance(tree.root, LeafNode)
    assert tree.root.leaf_class == 1
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

    child1 = tree1.copy()
    child2 = tree2.copy()
    assert isinstance(child2.root, InnerNode)
    genetic_operations._do_crossover_swap(child1, child2, child1.root, child2.root.children[0])

    result1, result2 = genetic_operations._check_max_depth(tree1, tree2, child1, child2, 2)
    assert result1 == child1
    assert result2 != child2
    assert isinstance(result2.root, InnerNode)
    assert result2.root.attribute == 0
    assert result2.root.threshold == 2.6
    assert isinstance(result2.root.children[0], LeafNode)
    assert isinstance(result2.root.children[1], LeafNode)
    assert result2.root.children[0].leaf_class == 1
    assert result2.root.children[1].leaf_class == 0
    assert result2.root.children[0].parent == result2.root
    assert result2.root.children[1].parent == result2.root

# Authors: Paweł Kochański, Jakub Proboszcz
# Written as a part of project in course UMA in semester 23Z

from tree import LeafNode, InnerNode, DecisionTree, print_tree
from io import StringIO
import pandas as pd
from sklearn.metrics import accuracy_score


def test_prediction():
    # example from initial documentation, pages 1-2
    # a_1 is attribute 0, a_2 is attribute 1
    leaf1 = LeafNode(1)
    leaf2 = LeafNode(0)
    leaf3 = LeafNode(1)
    inner = InnerNode(1, 2, children=(leaf2, leaf3))
    root = InnerNode(0, 4, children=(leaf1, inner))
    tree = DecisionTree(root)
    assert tree.predict((2, 3)) == 1
    assert tree.predict((5, 1)) == 0
    assert tree.predict((4, 2)) == 1


def test_prediction_dataframe():
    # example from initial documentation, pages 1-2
    # a_1 is attribute 0, a_2 is attribute 1
    leaf1 = LeafNode(1)
    leaf2 = LeafNode(0)
    leaf3 = LeafNode(1)
    inner = InnerNode(1, 2, children=(leaf2, leaf3))
    root = InnerNode(0, 4, children=(leaf1, inner))
    tree = DecisionTree(root)
    predictions = tree.predict(pd.DataFrame([(2, 3), (5, 1), (4, 2)], columns=['a1', 'a2'], index=[0, 1, 2]))
    assert accuracy_score([1, 0, 1], predictions) == 1.0


def test_prediction_multiclass_dataframe():
    leaf1 = LeafNode(0)
    leaf2 = LeafNode(1)
    leaf3 = LeafNode(2)
    inner = InnerNode(1, 2, children=(leaf2, leaf3))
    root = InnerNode(0, 4, children=(leaf1, inner))
    tree = DecisionTree(root)
    predictions = tree.predict(pd.DataFrame([(2, 3), (5, 1), (4, 2)], columns=['a1', 'a2'], index=[0, 1, 2]))
    assert accuracy_score([0, 1, 2], predictions) == 1.0


def test_leaf_trees():
    leaf1 = LeafNode(2)
    assert leaf1.predict((3, 2, 1)) == 2
    assert leaf1.predict((1, 2, 3)) == 2
    assert leaf1.predict((2, 2, 2)) == 2
    leaf1 = LeafNode(0)
    assert leaf1.predict((3, 2, 1)) == 0
    assert leaf1.predict((1, 2, 3)) == 0
    assert leaf1.predict((2, 2, 2)) == 0


def test_full_tree():
    # tree structure:
    #              (0|2)
    #      (1|2)           (1|2)
    #  (2|2)   (2|2)   (2|2)   (2|2)
    # [0] [1] [2] [3] [4] [5] [6] [7]
    leaf0 = LeafNode(0)
    leaf1 = LeafNode(1)
    leaf2 = LeafNode(2)
    leaf3 = LeafNode(3)
    leaf4 = LeafNode(4)
    leaf5 = LeafNode(5)
    leaf6 = LeafNode(6)
    leaf7 = LeafNode(7)
    inner3_1 = InnerNode(2, 2, children=(leaf0, leaf1))
    inner3_2 = InnerNode(2, 2, children=(leaf2, leaf3))
    inner3_3 = InnerNode(2, 2, children=(leaf4, leaf5))
    inner3_4 = InnerNode(2, 2, children=(leaf6, leaf7))
    inner2_1 = InnerNode(1, 2, children=(inner3_1, inner3_2))
    inner2_2 = InnerNode(1, 2, children=(inner3_3, inner3_4))
    root = InnerNode(0, 2, children=(inner2_1, inner2_2))
    tree = DecisionTree(root)
    assert tree.predict((1, 1, 1)) == 0
    assert tree.predict((1, 1, 3)) == 1
    assert tree.predict((1, 3, 1)) == 2
    assert tree.predict((1, 3, 3)) == 3
    assert tree.predict((3, 1, 1)) == 4
    assert tree.predict((3, 1, 3)) == 5
    assert tree.predict((3, 3, 1)) == 6
    assert tree.predict((3, 3, 3)) == 7


def test_print_tree():
    leaf1 = LeafNode(1)
    leaf2 = LeafNode(0)
    leaf3 = LeafNode(1)
    inner = InnerNode(1, 2, children=(leaf2, leaf3))
    root = InnerNode(0, 4, children=(leaf1, inner))
    stream = StringIO()
    tree = DecisionTree(root)
    print_tree(tree, file=stream)
    assert stream.getvalue() == \
        "     (0|4.00)      \n" + \
        "   [1]    (1|2.00) \n" + \
        "          [0]  [1] \n"


def test_print_full_tree():
    leaf0 = LeafNode(0)
    leaf1 = LeafNode(1)
    leaf2 = LeafNode(2)
    leaf3 = LeafNode(3)
    leaf4 = LeafNode(4)
    leaf5 = LeafNode(5)
    leaf6 = LeafNode(6)
    leaf7 = LeafNode(7)
    inner3_1 = InnerNode(2, 2, children=(leaf0, leaf1))
    inner3_2 = InnerNode(2, 2, children=(leaf2, leaf3))
    inner3_3 = InnerNode(2, 2, children=(leaf4, leaf5))
    inner3_4 = InnerNode(2, 2, children=(leaf6, leaf7))
    inner2_1 = InnerNode(1, 2, children=(inner3_1, inner3_2))
    inner2_2 = InnerNode(1, 2, children=(inner3_3, inner3_4))
    root = InnerNode(0, 2, children=(inner2_1, inner2_2))
    tree = DecisionTree(root)
    stream = StringIO()
    print_tree(tree, file=stream)
    assert stream.getvalue() == \
        "               (0|2.00)                \n" + \
        "     (1|2.00)            (1|2.00)      \n" + \
        "(2|2.00)  (2|2.00)  (2|2.00)  (2|2.00) \n" + \
        "[0]  [1]  [2]  [3]  [4]  [5]  [6]  [7] \n"


def test_subtree_nodes():
    leaf1 = LeafNode(1)
    leaf2 = LeafNode(0)
    leaf3 = LeafNode(1)
    inner = InnerNode(1, 2, children=(leaf2, leaf3))
    root = InnerNode(0, 4, children=(leaf1, inner))
    tree = DecisionTree(root)
    assert [node for node in tree.nodes()] == [root, leaf1, inner, leaf2, leaf3]
    assert [node for node in root.subtree_nodes()] == [root, leaf1, inner, leaf2, leaf3]
    assert [node for node in inner.subtree_nodes()] == [inner, leaf2, leaf3]


def test_depth():
    leaf1 = LeafNode(1)
    leaf2 = LeafNode(0)
    leaf3 = LeafNode(1)
    inner = InnerNode(1, 2, children=(leaf2, leaf3))
    root = InnerNode(0, 4, children=(leaf1, inner))
    tree = DecisionTree(root)
    assert root.depth() == 0
    assert leaf1.depth() == 1
    assert inner.depth() == 1
    assert leaf2.depth() == 2
    assert leaf3.depth() == 2
    assert tree.depth() == 2


def test_copy():
    leaf1 = LeafNode(1)
    leaf2 = LeafNode(0)
    leaf3 = LeafNode(1)
    inner = InnerNode(1, 2, children=(leaf2, leaf3))
    root = InnerNode(0, 4, children=(leaf1, inner))
    tree = DecisionTree(root)
    copied = tree.copy()
    assert tree != copied
    assert tree.root != copied.root
    assert isinstance(copied.root, InnerNode)
    assert copied.root.attribute == 0
    assert copied.root.threshold == 4

    assert leaf1 != copied.root.children[0]
    assert isinstance(copied.root.children[0], LeafNode)
    assert copied.root.children[0].leaf_class == 1

    assert inner != copied.root.children[1]
    assert isinstance(copied.root.children[1], InnerNode)
    assert copied.root.children[1].attribute == 1
    assert copied.root.children[1].threshold == 2

    assert leaf2 != copied.root.children[1].children[0]
    assert isinstance(copied.root.children[1].children[0], LeafNode)
    assert copied.root.children[1].children[0].leaf_class == 0

    assert leaf3 != copied.root.children[1].children[1]
    assert isinstance(copied.root.children[1].children[1], LeafNode)
    assert copied.root.children[1].children[1].leaf_class == 1


def test_recalculate_no_structure_change():
    X_train = pd.DataFrame([(3, 2), (1, 4), (4, 1)], index=[0, 1, 2], columns=['a', 'b'])
    y_train = pd.Series([0, 0, 1], index=[0, 1, 2])
    leaf1 = LeafNode(1, pd.DataFrame([(3, 2)], index=[0], columns=['a', 'b']), pd.Series([1], index=[0]))
    leaf2 = LeafNode(None)
    leaf3 = LeafNode(None)
    inner = InnerNode(1, 2, children=(leaf2, leaf3))
    root = InnerNode(0, 2, (leaf1, inner), X_train, y_train)
    root.recalculate()

    assert leaf1.leaf_class == 0
    assert leaf1.X_train.values[0][0] == 1
    assert leaf1.X_train.values[0][1] == 4
    assert leaf1.y_train.values[0] == 0

    assert leaf2.leaf_class == 1
    assert leaf2.X_train.values[0][0] == 4
    assert leaf2.X_train.values[0][1] == 1
    assert leaf2.y_train.values[0] == 1

    assert leaf3.leaf_class == 0
    assert leaf3.X_train.values[0][0] == 3
    assert leaf3.X_train.values[0][1] == 2
    assert leaf3.y_train.values[0] == 0

    assert inner.X_train.values[0][0] == 3
    assert inner.X_train.values[0][1] == 2
    assert inner.y_train.values[0] == 0

    assert inner.X_train.values[1][0] == 4
    assert inner.X_train.values[1][1] == 1
    assert inner.y_train.values[1] == 1


def test_recalculate_inner_node_rolled_up():
    X_train = pd.DataFrame([(3, 2), (1, 4), (4, 1)], index=[0, 1, 2], columns=['a', 'b'])
    y_train = pd.Series([0, 0, 1], index=[0, 1, 2])
    leaf1 = LeafNode(1, pd.DataFrame([(3, 2)], index=[0], columns=['a', 'b']), pd.Series([1], index=[0]))
    leaf2 = LeafNode(None)
    leaf3 = LeafNode(None)
    inner = InnerNode(1, 2, children=(leaf2, leaf3))
    root = InnerNode(0, 4, (leaf1, inner), X_train, y_train)
    root.recalculate()

    assert leaf1 == root.children[0]
    assert leaf1.leaf_class == 0
    assert leaf1.X_train.values[0][0] == 3
    assert leaf1.X_train.values[0][1] == 2
    assert leaf1.y_train.values[0] == 0
    assert leaf1.X_train.values[1][0] == 1
    assert leaf1.X_train.values[1][1] == 4
    assert leaf1.y_train.values[1] == 0

    assert inner != root.children[1]
    assert isinstance(root.children[1], LeafNode)
    assert root.children[1].leaf_class == 1
    assert root.children[1].X_train.values[0][0] == 4
    assert root.children[1].X_train.values[0][1] == 1
    assert root.children[1].y_train.values[0] == 1

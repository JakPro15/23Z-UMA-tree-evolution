from tree import LeafNode, InnerNode, print_tree
from io import StringIO


def test_prediction():
    # example from initial documentation, pages 1-2
    # a_1 is attribute 0, a_2 is attribute 1
    leaf1 = LeafNode(1)
    leaf2 = LeafNode(0)
    leaf3 = LeafNode(1)
    inner = InnerNode(1, 2, children=(leaf2, leaf3))
    root = InnerNode(0, 4, children=(leaf1, inner))
    assert root.predict((2, 3)) == 1
    assert root.predict((5, 1)) == 0
    assert root.predict((4, 2)) == 1


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
    assert root.predict((1, 1, 1)) == 0
    assert root.predict((1, 1, 3)) == 1
    assert root.predict((1, 3, 1)) == 2
    assert root.predict((1, 3, 3)) == 3
    assert root.predict((3, 1, 1)) == 4
    assert root.predict((3, 1, 3)) == 5
    assert root.predict((3, 3, 1)) == 6
    assert root.predict((3, 3, 3)) == 7


def test_print_tree():
    leaf1 = LeafNode(1)
    leaf2 = LeafNode(0)
    leaf3 = LeafNode(1)
    inner = InnerNode(1, 2, children=(leaf2, leaf3))
    root = InnerNode(0, 4, children=(leaf1, inner))
    stream = StringIO()
    print_tree(root, file=stream)
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
    stream = StringIO()
    print_tree(root, file=stream)
    assert stream.getvalue() == \
        "               (0|2.00)                \n" + \
        "     (1|2.00)            (1|2.00)      \n" + \
        "(2|2.00)  (2|2.00)  (2|2.00)  (2|2.00) \n" + \
        "[0]  [1]  [2]  [3]  [4]  [5]  [6]  [7] \n"

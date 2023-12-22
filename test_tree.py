from tree import LeafNode, InnerNode


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

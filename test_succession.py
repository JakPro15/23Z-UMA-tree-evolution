# Authors: Paweł Kochański, Jakub Proboszcz
# Written as a part of project in course UMA in semester 23z

import succession
from tree import DecisionTree, LeafNode

def test_generation_succesion():
    population = [DecisionTree(LeafNode(k)) for k in range(5)]
    gen_op_population = [DecisionTree(LeafNode(k)) for k in range(5)]
    scores = list(range(5))
    gen_op_scores = list(range(5))

    assert succession.generational_succession(population, gen_op_population, scores, gen_op_scores) == (gen_op_population, gen_op_scores)

def test_elite_succesion_no_elite():
    population = [DecisionTree(LeafNode(k)) for k in range(5)]
    gen_op_population = [DecisionTree(LeafNode(k)) for k in range(5)]
    scores = list(range(5))
    gen_op_scores = list(range(5))

    elite_pop, elite_scores = succession.elite_succession(population, gen_op_population, scores, gen_op_scores, 0)

    for i in range(len(elite_pop)):
        assert elite_pop[i] == gen_op_population[-1 * (i + 1)]

    for i in range(len(elite_pop)):
        assert elite_scores[i] == gen_op_scores[-1 * (i + 1)]

def test_elite_succesion():
    population = [DecisionTree(LeafNode(k)) for k in range(5)]
    gen_op_population = [DecisionTree(LeafNode(k)) for k in range(5)]
    scores = list(range(5))
    gen_op_scores = list(range(5))

    elite_size = 2

    elite_pop, elite_scores = succession.elite_succession(population, gen_op_population, scores, gen_op_scores, elite_size)

    for i in range(elite_size):
        assert population[-1 * (i + 1)] == elite_pop[i]

    for i in range(elite_size):
        assert scores[-1 * (i + 1)] == elite_scores[i]

    for i in range(len(gen_op_population) - elite_size):
        assert gen_op_population[-1 * (i + 1)] == elite_pop[i + elite_size]

    for i in range(len(gen_op_population) - elite_size):
        assert gen_op_scores[-1 * (i + 1)] == elite_scores[i + elite_size]
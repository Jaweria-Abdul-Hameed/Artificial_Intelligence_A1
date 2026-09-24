"""Behavior checks for greedyBestFirstSearch (AI-04); q-tests don't cover it.

Run from anywhere: python search/search/test_gbfs.py
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import search


class GraphProblem(search.SearchProblem):
    def __init__(self, edges, start, goal):
        self.edges, self.start, self.goal = edges, start, goal

    def getStartState(self):
        return self.start

    def isGoalState(self, state):
        return state == self.goal

    def getSuccessors(self, state):
        return self.edges.get(state, [])


# S->A looks closer to the goal (h=1) but A->G is expensive; S->B->G is cheaper.
TRAP = {'S': [('A', 'a', 1), ('B', 'b', 1)],
        'A': [('G', 'g', 10)],
        'B': [('G', 'g', 1)]}
H = {'S': 5, 'A': 1, 'B': 3, 'G': 0}


def h(state, problem=None):
    return H[state]


class GreedyBestFirstTest(unittest.TestCase):
    def test_follows_lowest_h_not_lowest_total_cost(self):
        problem = GraphProblem(TRAP, 'S', 'G')
        self.assertEqual(search.greedyBestFirstSearch(problem, h), ['a', 'g'])

    def test_astar_finds_the_cheaper_path_on_the_same_graph(self):
        problem = GraphProblem(TRAP, 'S', 'G')
        self.assertEqual(search.aStarSearch(problem, h), ['b', 'g'])

    def test_start_is_goal_returns_empty_plan(self):
        problem = GraphProblem({}, 'S', 'S')
        self.assertEqual(search.greedyBestFirstSearch(problem, h), [])

    def test_unsolvable_and_cyclic_graph_terminates_with_empty_plan(self):
        edges = {'S': [('A', 'a', 1)], 'A': [('S', 's', 1)]}
        problem = GraphProblem(edges, 'S', 'G')
        self.assertEqual(search.greedyBestFirstSearch(problem, h), [])

    def test_gbfs_abbreviation(self):
        self.assertIs(search.gbfs, search.greedyBestFirstSearch)


if __name__ == '__main__':
    unittest.main()

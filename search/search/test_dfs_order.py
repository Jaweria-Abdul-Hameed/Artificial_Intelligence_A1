"""Checks for the opt-in N->E->S->W ordering in search.py (AI-01).

Run from this folder: python test_dfs_order.py
"""
import unittest

import search


class StarProblem(search.SearchProblem):
    """Start state 'S' with one successor per direction; none is a goal."""

    def __init__(self):
        self.expanded = []

    def getStartState(self):
        return 'S'

    def isGoalState(self, state):
        self.expanded.append(state)
        return False

    def getSuccessors(self, state):
        if state != 'S':
            return []
        return [('N', 'North', 1), ('S2', 'South', 1),
                ('E', 'East', 1), ('W', 'West', 1)]


class ReorderSuccessorsTest(unittest.TestCase):
    def test_sorts_north_east_south_west(self):
        succ = [(1, 'West', 1), (2, 'South', 1), (3, 'East', 1), (4, 'North', 1)]
        self.assertEqual([s[1] for s in search.reorderSuccessors(succ)],
                         ['North', 'East', 'South', 'West'])

    def test_non_direction_actions_go_last_in_original_order(self):
        succ = [(1, 'X1', 1), (2, 'West', 1), (3, 'X2', 1), (4, 'North', 1)]
        self.assertEqual([s[1] for s in search.reorderSuccessors(succ)],
                         ['North', 'West', 'X1', 'X2'])


class DfsOrderTest(unittest.TestCase):
    def test_dfsNESW_expands_north_first(self):
        problem = StarProblem()
        search.dfsNESW(problem)
        self.assertEqual(problem.expanded, ['S', 'N', 'E', 'S2', 'W'])

    def test_default_dfs_keeps_natural_order(self):
        problem = StarProblem()
        original = search.ENFORCE_NESW_DFS
        search.ENFORCE_NESW_DFS = False
        try:
            search.dfs(problem)
        finally:
            search.ENFORCE_NESW_DFS = original
        # natural order pushed N, S2, E, W -> LIFO pops W first
        self.assertEqual(problem.expanded, ['S', 'W', 'E', 'S2', 'N'])

    def test_flag_true_makes_dfs_north_first(self):
        problem = StarProblem()
        original = search.ENFORCE_NESW_DFS
        search.ENFORCE_NESW_DFS = True
        try:
            search.dfs(problem)
        finally:
            search.ENFORCE_NESW_DFS = original
        self.assertEqual(problem.expanded, ['S', 'N', 'E', 'S2', 'W'])


if __name__ == '__main__':
    unittest.main()

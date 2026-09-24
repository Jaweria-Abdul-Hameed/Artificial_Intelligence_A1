"""Edge-case and criterion checks for the search algorithms and CornersProblem
(AI-01 .. AI-07) that the autograder does not cover.

Run from anywhere: python search/search/test_search_edges.py
"""
import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import layout
import pacman
import search
import searchAgents
import util
from graph_problem import GraphProblem


ALGORITHMS = {
    'dfs': search.depthFirstSearch,
    'bfs': search.breadthFirstSearch,
    'ucs': search.uniformCostSearch,
    'gbfs': search.greedyBestFirstSearch,
    'astar': search.aStarSearch,
}


class EveryAlgorithmTest(unittest.TestCase):
    def test_start_is_goal_returns_empty_plan(self):
        for name, fn in ALGORITHMS.items():
            with self.subTest(name):
                self.assertEqual(fn(GraphProblem({}, 'S', 'S')), [])

    def test_unsolvable_cyclic_graph_returns_empty_plan(self):
        edges = {'S': [('A', 'a', 1)], 'A': [('S', 's', 1)]}
        for name, fn in ALGORITHMS.items():
            with self.subTest(name):
                self.assertEqual(fn(GraphProblem(edges, 'S', 'G')), [])


class DfsTest(unittest.TestCase):
    def test_is_iterative_so_a_deep_chain_hits_no_recursion_limit(self):
        n = 5000  # well above Python's default recursion limit (1000)
        edges = {i: [(i + 1, 'East', 1)] for i in range(n)}
        plan = search.depthFirstSearch(GraphProblem(edges, 0, n))
        self.assertEqual(len(plan), n)

    def test_never_expands_a_state_twice(self):
        expanded = []

        class Diamond(GraphProblem):
            def getSuccessors(self, state):
                expanded.append(state)
                return super().getSuccessors(state)

        edges = {'S': [('A', 'a', 1), ('B', 'b', 1)],
                 'A': [('C', 'c', 1)], 'B': [('C', 'c', 1)], 'C': []}
        search.depthFirstSearch(Diamond(edges, 'S', 'G'))
        self.assertEqual(len(expanded), len(set(expanded)))


class BfsUcsTest(unittest.TestCase):
    # S->G direct costs 10 (1 step); S->A->G costs 2 (2 steps).
    EDGES = {'S': [('G', 'direct', 10), ('A', 'a', 1)], 'A': [('G', 'g', 1)]}

    def test_bfs_returns_fewest_steps(self):
        plan = search.breadthFirstSearch(GraphProblem(self.EDGES, 'S', 'G'))
        self.assertEqual(plan, ['direct'])

    def test_ucs_returns_cheapest_not_fewest_steps(self):
        plan = search.uniformCostSearch(GraphProblem(self.EDGES, 'S', 'G'))
        self.assertEqual(plan, ['a', 'g'])

    def test_ucs_lowers_cost_of_a_state_already_on_the_fringe(self):
        # C is first discovered via B at cost 4, then via A at cost 2.
        edges = {'S': [('B', 'b', 1), ('A', 'a', 1)], 'B': [('C', 'c', 3)],
                 'A': [('C', 'c', 1)], 'C': [('G', 'g', 1)]}
        updates, pops = [], []
        RealQueue = util.PriorityQueue  # the patch below replaces util's name

        class SpyQueue(RealQueue):
            def update(self, item, priority):
                updates.append((item, priority))
                RealQueue.update(self, item, priority)

            def pop(self):
                item = RealQueue.pop(self)
                pops.append(item)
                return item

        with mock.patch.object(util, 'PriorityQueue', SpyQueue):
            plan = search.uniformCostSearch(GraphProblem(edges, 'S', 'G'))
        self.assertEqual(plan, ['a', 'c', 'g'])
        self.assertIn(('C', 4), updates)
        self.assertIn(('C', 2), updates)   # decrease-key, not a second push
        self.assertEqual(pops.count('C'), 1)  # C is queued/expanded once


class AStarTest(unittest.TestCase):
    def test_reopens_states_so_inconsistent_admissible_h_stays_optimal(self):
        # h(A)=6 is exact (admissible) but h(A) > cost(A,C)+h(C): inconsistent.
        # C is closed first via B at g=4, then reached cheaper via A at g=2.
        edges = {'S': [('A', 'a', 1), ('B', 'b', 1)], 'A': [('C', 'c', 1)],
                 'B': [('C', 'c', 3)], 'C': [('G', 'g', 5)]}
        H = {'S': 0, 'A': 6, 'B': 0, 'C': 0, 'G': 0}
        plan = search.aStarSearch(GraphProblem(edges, 'S', 'G'),
                                  lambda s, problem=None: H[s])
        self.assertEqual(plan, ['a', 'c', 'g'])  # cost 7, not 9 via B

    def test_passes_the_problem_to_the_heuristic(self):
        problem = GraphProblem({'S': [('G', 'g', 1)]}, 'S', 'G')
        seen = []
        search.aStarSearch(problem, lambda s, p=None: seen.append(p) or 0)
        self.assertTrue(seen and all(p is problem for p in seen))


class CornersProblemTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # layout.getLayout looks for layouts/ relative to the working directory
        cls._cwd = os.getcwd()
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

    @classmethod
    def tearDownClass(cls):
        os.chdir(cls._cwd)

    def setUp(self):
        state = pacman.GameState()
        state.initialize(layout.getLayout('tinyCorners'), 0)
        self.problem = searchAgents.CornersProblem(state)

    def test_start_state_is_position_and_empty_tuple(self):
        position, visited = self.problem.getStartState()
        self.assertEqual(position, self.problem.startingPosition)
        self.assertEqual(visited, ())
        self.assertIsInstance(visited, tuple)

    def test_goal_only_when_all_four_corners_visited(self):
        corners = self.problem.corners
        self.assertTrue(self.problem.isGoalState(((1, 1), corners)))
        self.assertFalse(self.problem.isGoalState(((1, 1), corners[:3])))

    def test_get_successors_counts_one_expansion_per_call(self):
        before = self.problem._expanded
        self.problem.getSuccessors(self.problem.getStartState())
        self.assertEqual(self.problem._expanded, before + 1)

    def test_successor_keeps_visited_corners_in_canonical_order(self):
        first, last = self.problem.corners[0], self.problem.corners[3]
        x, y = first
        # already visited corners[3]; step onto corners[0] from beside it.
        # Canonical order is corners order, not arrival order.
        state = ((x + 1, y), (last,))
        nextStates = {s[0][0]: s[0] for s in self.problem.getSuccessors(state)}
        self.assertEqual(nextStates[first][1], (first, last))

    def test_start_on_a_corner_counts_that_corner_as_visited(self):
        corner = self.problem.corners[1]
        self.problem.startingPosition = corner
        self.assertEqual(self.problem.getStartState(), (corner, (corner,)))

    def test_successors_are_exactly_the_open_neighbours_everywhere(self):
        walls = self.problem.walls
        for x in range(walls.width):
            for y in range(walls.height):
                if walls[x][y]:
                    continue
                expected = {(x + dx, y + dy)
                            for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0))
                            if not walls[x + dx][y + dy]}
                got = {s[0][0] for s in self.problem.getSuccessors(((x, y), ()))}
                self.assertEqual(got, expected, (x, y))


if __name__ == '__main__':
    unittest.main()

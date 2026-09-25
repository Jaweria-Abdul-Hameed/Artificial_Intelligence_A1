"""Behavior checks for the CSV trace logger (AI-09); q-tests don't cover it.

Run from anywhere: python search/search/test_csv_logger.py
"""
import csv
import glob
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import search
from graph_problem import GraphProblem

EDGES = {'S': [('A', 'a', 1), ('B', 'b', 1)],
         'A': [('G', 'g', 10)],
         'B': [('G', 'g', 1)]}
H = {'S': 5, 'A': 1, 'B': 3, 'G': 0}
COLUMNS = ['iteration', 'expanded_state', 'parent', 'action', 'generated_successors',
           'frontier_before', 'frontier_after', 'explored', 'g', 'h', 'f']

ALGORITHMS = {
    'dfs': lambda p: search.depthFirstSearch(p),
    'bfs': lambda p: search.breadthFirstSearch(p),
    'ucs': lambda p: search.uniformCostSearch(p),
    'gbfs': lambda p: search.greedyBestFirstSearch(p, lambda s, pr=None: H[s]),
    'astar': lambda p: search.aStarSearch(p, lambda s, pr=None: H[s]),
}


class CsvLoggerTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        os.environ['SEARCH_LOG'] = '1'
        os.environ['SEARCH_LOG_DIR'] = self.dir

    def tearDown(self):
        os.environ.pop('SEARCH_LOG', None)
        os.environ.pop('SEARCH_LOG_DIR', None)

    def rows(self, name):
        files = glob.glob(os.path.join(self.dir, name + '_*.csv'))
        self.assertEqual(len(files), 1, files)
        with open(files[0], newline='') as fh:
            return list(csv.DictReader(fh))

    def test_every_algorithm_writes_exact_columns_and_no_blank_numbers(self):
        for name, run in ALGORITHMS.items():
            run(GraphProblem(EDGES, 'S', 'G'))
            files = glob.glob(os.path.join(self.dir, name + '_*.csv'))
            with open(files[0], newline='') as fh:
                reader = csv.DictReader(fh)
                rows = list(reader)
                self.assertEqual(reader.fieldnames, COLUMNS, name)
            self.assertTrue(rows, name)
            self.assertEqual([r['iteration'] for r in rows],
                             [str(i) for i in range(1, len(rows) + 1)], name)
            for r in rows:
                for col in ('g', 'h', 'f'):
                    self.assertNotIn(r[col], ('', 'None'), (name, col))

    def test_dfs_and_bfs_use_h_zero_and_f_equals_g(self):
        for name in ('dfs', 'bfs', 'ucs'):
            ALGORITHMS[name](GraphProblem(EDGES, 'S', 'G'))
            for r in self.rows(name):
                self.assertEqual(r['h'], '0')
                self.assertEqual(r['f'], r['g'])

    def test_astar_logs_f_as_g_plus_h_and_tracks_parent(self):
        ALGORITHMS['astar'](GraphProblem(EDGES, 'S', 'G'))
        rows = self.rows('astar')
        # h is inconsistent here, so A (f=2) is expanded before B (f=4)
        self.assertEqual([r['expanded_state'] for r in rows], ['S', 'A', 'B', 'G'])
        self.assertEqual(rows[2]['parent'], 'S')
        self.assertEqual(rows[2]['action'], 'b')
        self.assertEqual(rows[3]['parent'], 'B')
        self.assertEqual(rows[3]['g'], '2')
        for r in rows:
            self.assertEqual(int(r['f']), int(r['g']) + int(r['h']))

    def test_frontier_and_explored_snapshots(self):
        ALGORITHMS['bfs'](GraphProblem(EDGES, 'S', 'G'))
        rows = self.rows('bfs')
        self.assertEqual(rows[0]['frontier_before'], '[S]')
        self.assertEqual(rows[0]['explored'], '[]')
        self.assertIn('A', rows[0]['frontier_after'])
        self.assertIn('B', rows[0]['frontier_after'])
        self.assertEqual(rows[1]['explored'], '[S]')

    def test_logging_never_changes_the_returned_plan(self):
        for name, run in ALGORITHMS.items():
            os.environ['SEARCH_LOG'] = '0'
            plain = run(GraphProblem(EDGES, 'S', 'G'))
            os.environ['SEARCH_LOG'] = '1'
            logged = run(GraphProblem(EDGES, 'S', 'G'))
            self.assertEqual(plain, logged, name)

    def test_disabled_writes_nothing(self):
        os.environ['SEARCH_LOG'] = '0'
        for run in ALGORITHMS.values():
            run(GraphProblem(EDGES, 'S', 'G'))
        self.assertEqual(os.listdir(self.dir), [])

    def test_helper_searches_with_visualize_false_are_not_logged(self):
        problem = GraphProblem(EDGES, 'S', 'G')
        problem.visualize = False
        search.breadthFirstSearch(problem)
        self.assertEqual(os.listdir(self.dir), [])


if __name__ == '__main__':
    unittest.main()

"""Regenerate every CSV trace, screenshot and metric used by the report.

Usage (from the repo root):  python tools/run_experiments.py [--no-shots]

For each experiment it runs pacman.py twice inside search/search:
  * quiet (-q)  -> the CSV trace lands in evidence/ (logger is on under pacman.py)
                   and the printed cost / nodes / time are parsed for the tables
  * graphics    -> tools/snap.py saves evidence/screenshots/<label>.png
Metrics go to tools/results.json.  Repo-level helper; not part of the submission ZIP.
"""
import glob
import json
import os
import re
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT = os.path.join(ROOT, 'search', 'search')
EVIDENCE = os.path.join(PROJECT, 'evidence')
SHOTS = os.path.join(EVIDENCE, 'screenshots')
SNAP = os.path.join(ROOT, 'tools', 'snap.py')
CUSTOM = '24i3025Search'

# (label, task, description, pacman.py arguments)
EXPERIMENTS = [
    ('dfs_tinyMaze', 'Task 1', 'DFS tinyMaze', '-l tinyMaze -p SearchAgent -a fn=dfs'),
    ('dfs_mediumMaze', 'Task 1', 'DFS mediumMaze', '-l mediumMaze -p SearchAgent -a fn=dfs'),
    ('dfs_bigMaze', 'Task 1', 'DFS bigMaze', '-l bigMaze -z .5 -p SearchAgent -a fn=dfs'),
    ('dfsNESW_mediumMaze', 'Task 1', 'DFS N-E-S-W order mediumMaze',
     '-l mediumMaze -p SearchAgent -a fn=dfsNESW'),
    ('bfs_mediumMaze', 'Task 2', 'BFS mediumMaze', '-l mediumMaze -p SearchAgent -a fn=bfs'),
    ('bfs_bigMaze', 'Task 2', 'BFS bigMaze', '-l bigMaze -z .5 -p SearchAgent -a fn=bfs'),
    ('ucs_mediumMaze', 'Task 3', 'UCS mediumMaze', '-l mediumMaze -p SearchAgent -a fn=ucs'),
    ('ucs_mediumMaze_z', 'Task 3', 'UCS mediumMaze (substitute for mediumDenselyMaze)',
     '-l mediumMaze -p SearchAgent -a fn=ucs -z .5'),
    ('ucs_stayEast', 'Task 3', 'UCS StayEastSearchAgent mediumMaze',
     '-l mediumMaze -p StayEastSearchAgent'),
    ('gbfs_bigMaze', 'Task 4', 'GBFS bigMaze (Manhattan)',
     '-l bigMaze -z .5 -p SearchAgent -a fn=gbfs,heuristic=manhattanHeuristic'),
    ('gbfs_bigMaze_euclid', 'Task 4', 'GBFS bigMaze (Euclidean)',
     '-l bigMaze -z .5 -p SearchAgent -a fn=gbfs,heuristic=euclideanHeuristic'),
    ('astar_bigMaze_null', 'Task 5', 'A* bigMaze (null heuristic)',
     '-l bigMaze -z .5 -p SearchAgent -a fn=astar,heuristic=nullHeuristic'),
    ('astar_bigMaze', 'Task 5', 'A* bigMaze (Manhattan)',
     '-l bigMaze -z .5 -p SearchAgent -a fn=astar,heuristic=manhattanHeuristic'),
    ('bfs_tinyCorners', 'Task 6', 'BFS CornersProblem tinyCorners',
     '-l tinyCorners -p SearchAgent -a fn=bfs,prob=CornersProblem'),
    ('astar_mediumCorners', 'Task 6', 'A* corners mediumCorners',
     '-l mediumCorners -p AStarCornersAgent -z .5'),
    ('astar_trickySearch', 'Task 7', 'A* food trickySearch',
     '-l trickySearch -p AStarFoodSearchAgent'),
    ('bfs_bigSearch', 'Task 7', 'ClosestDot bigSearch', '-l bigSearch -p ClosestDotSearchAgent'),
    ('custom_dfs', 'Custom', 'DFS custom maze', '-l %s -p SearchAgent -a fn=dfs' % CUSTOM),
    ('custom_bfs', 'Custom', 'BFS custom maze', '-l %s -p SearchAgent -a fn=bfs' % CUSTOM),
    ('custom_ucs', 'Custom', 'UCS custom maze', '-l %s -p SearchAgent -a fn=ucs' % CUSTOM),
    ('custom_gbfs', 'Custom', 'GBFS custom maze',
     '-l %s -p SearchAgent -a fn=gbfs,heuristic=manhattanHeuristic' % CUSTOM),
    ('custom_astar', 'Custom', 'A* custom maze',
     '-l %s -p SearchAgent -a fn=astar,heuristic=manhattanHeuristic' % CUSTOM),
]

# File-name label for runs that would otherwise share algorithm + layout
TAGS = {'ucs_mediumMaze_z': 'zoom', 'ucs_stayEast': 'StayEastSearchAgent',
        'gbfs_bigMaze': 'manhattan', 'gbfs_bigMaze_euclid': 'euclidean',
        'astar_bigMaze': 'manhattan', 'astar_bigMaze_null': 'null'}

# Literal PDF commands that reference files that do not exist (Inconsistency #4).
BROKEN = [
    ('pdf_mediumDenselyMaze', '-l mediumDenselyMaze -p SearchAgent -a fn=ucs'),
    ('pdf_stayEastSearch', '-l stayEastSearch -p SearchAgent -a fn=ucs'),
]


def run(args, timeout=600, tag=''):
    start = time.time()
    env = dict(os.environ, SEARCH_LOG_TAG=tag)
    proc = subprocess.run([sys.executable, 'pacman.py'] + args.split(), env=env,
                          cwd=PROJECT, capture_output=True, text=True, timeout=timeout)
    return proc, time.time() - start


def parse(text):
    def num(pattern):
        m = re.search(pattern, text)
        return float(m.group(1)) if m else None
    return {
        'cost': num(r'(?:total cost of|with cost) (\d+)'),
        'nodes': num(r'Search nodes expanded: (\d+)'),
        'seconds': num(r'in ([\d.]+) seconds'),
        'score': num(r'Average Score: (-?[\d.]+)'),
    }


def main():
    shots = '--no-shots' not in sys.argv
    os.makedirs(SHOTS, exist_ok=True)
    for old in glob.glob(os.path.join(EVIDENCE, '*.csv')):
        os.remove(old)
    results = []
    for label, task, desc, args in EXPERIMENTS:
        before = set(glob.glob(os.path.join(EVIDENCE, '*.csv')))
        proc, wall = run(args + ' -q', tag=TAGS.get(label, ''))
        made = sorted(set(glob.glob(os.path.join(EVIDENCE, '*.csv'))) - before)
        row = {'label': label, 'task': task, 'description': desc, 'command': 'python pacman.py ' + args,
               'csv': [os.path.basename(p) for p in made], 'returncode': proc.returncode}
        row.update(parse(proc.stdout))
        if proc.returncode != 0:
            row['error'] = proc.stderr.strip().splitlines()[-1:] or proc.stdout.strip().splitlines()[-1:]
        if shots:
            shot = os.path.join(SHOTS, label + '.png')
            subprocess.run([sys.executable, SNAP, shot] + args.split() + ['--frameTime', '0'],
                           cwd=PROJECT, capture_output=True, text=True, timeout=900)
            row['screenshot'] = 'screenshots/%s.png' % label if os.path.exists(shot) else None
        results.append(row)
        print('%-22s cost=%s nodes=%s csv=%d' % (label, row['cost'], row['nodes'], len(made)))
    broken = []
    for label, args in BROKEN:
        proc, _ = run(args + ' -q', timeout=60)
        tail = (proc.stderr or proc.stdout).strip().splitlines()[-1:]
        broken.append({'label': label, 'command': 'python pacman.py ' + args,
                       'returncode': proc.returncode, 'message': tail})
    grader = subprocess.run([sys.executable, 'autograder.py', '--no-graphics'], cwd=PROJECT,
                            capture_output=True, text=True, timeout=900).stdout
    questions = [{'q': m[0], 'got': float(m[1]), 'max': float(m[2])}
                 for m in re.findall(r'^Question (q\d): ([\d.]+)/([\d.]+) ?$', grader, re.M)]
    total = re.search(r'^Total: ([\d.]+)/([\d.]+)', grader, re.M)
    autograder = {'questions': questions,
                  'total': [float(total.group(1)), float(total.group(2))] if total else None}
    with open(os.path.join(ROOT, 'tools', 'results.json'), 'w') as fh:
        json.dump({'experiments': results, 'broken': broken, 'autograder': autograder}, fh, indent=2)
    print('wrote tools/results.json')


if __name__ == '__main__':
    main()

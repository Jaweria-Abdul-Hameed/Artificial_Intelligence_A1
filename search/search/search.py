# search.py
# ---------


"""
In search.py, you will implement generic search algorithms which are called by
Pacman agents (in searchAgents.py).
"""

import util

class SearchProblem:
    """
    This class outlines the structure of a search problem, but doesn't implement
    any of the methods (in object-oriented terminology: an abstract class).

    You do not need to change anything in this class, ever.
    """

    def getStartState(self):
        """
        Returns the start state for the search problem.
        """
        util.raiseNotDefined()

    def isGoalState(self, state):
        """
          state: Search state

        Returns True if and only if the state is a valid goal state.
        """
        util.raiseNotDefined()

    def getSuccessors(self, state):
        """
          state: Search state

        For a given state, this should return a list of triples, (successor,
        action, stepCost), where 'successor' is a successor to the current
        state, 'action' is the action required to get there, and 'stepCost' is
        the incremental cost of expanding to that successor.
        """
        util.raiseNotDefined()

    def getCostOfActions(self, actions):
        """
         actions: A list of actions to take

        This method returns the total cost of a particular sequence of actions.
        The sequence must be composed of legal moves.
        """
        util.raiseNotDefined()


def tinyMazeSearch(problem):
    """
    Returns a sequence of moves that solves tinyMaze.  For any other maze, the
    sequence of moves will be incorrect, so only use this for tinyMaze.
    """
    from game import Directions
    s = Directions.SOUTH
    w = Directions.WEST
    return  [s, s, w, s, w, w, s, w]

# --- CSV trace logging (Section 3) -------------------------------------------
# One shared SearchLogger is used by all five algorithms.  Each algorithm keeps
# its own loop and only calls the logger from inside it; logging is a pure side
# effect and never changes what a search returns.
#
# Rows go to evidence/<algorithm>_<layout>_<timestamp>.csv (next to search.py).
# Logging is ON when the program is started through pacman.py and OFF under the
# autograder / when imported (so tests don't litter evidence/).  Set the
# environment variable SEARCH_LOG=1 to force it on or SEARCH_LOG=0 to force it
# off.  Internal helper searches (mazeDistance inside foodHeuristic, which builds
# its problem with visualize=False) are never logged.  ClosestDotSearchAgent runs
# one BFS per dot; all of them are appended to a single file per run.
CSV_COLUMNS = ['iteration', 'expanded_state', 'parent', 'action',
               'generated_successors', 'frontier_before', 'frontier_after',
               'explored', 'g', 'h', 'f']

def _loggingEnabled(problem):
    import os, sys
    flag = os.environ.get('SEARCH_LOG')
    if flag is not None:
        on = flag == '1'
    else:
        on = os.path.basename(sys.argv[0]) == 'pacman.py'
    return on and getattr(problem, 'visualize', True)

def _layoutName():
    import sys
    args = sys.argv[1:]
    for i, arg in enumerate(args):
        if arg in ('-l', '--layout') and i + 1 < len(args):
            return args[i + 1]
        if arg.startswith('--layout='):
            return arg.split('=', 1)[1]
    return 'unknown'

def _fmtState(state):
    """Compact text for a state; food grids are shown as (position, dots left)."""
    if isinstance(state, tuple) and len(state) == 2 and hasattr(state[1], 'count')             and hasattr(state[1], 'asList'):
        return '(%s, food=%d)' % (state[0], state[1].count())
    return str(state)

class SearchLogger:
    """Collects one row per expanded state and writes the CSV when finished."""
    _appendFiles = {}   # (algorithm, layout) -> path, for repeated sub-searches
    _appendCount = {}   # (algorithm, layout) -> iterations already written there

    def __init__(self, algorithm, problem):
        self.enabled = _loggingEnabled(problem)
        if not self.enabled:
            return
        import os
        self.algorithm = algorithm
        self.rows = []
        self.iteration = 0
        self.parents = {}    # state -> (parent state, action) of its latest generation
        self.costs = {}      # state -> g(n) along that latest generation
        self.explored = []
        self.dir = os.environ.get('SEARCH_LOG_DIR') or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'evidence')
        self.append = type(problem).__name__ == 'AnyFoodSearchProblem'
        self.key = (algorithm, _layoutName())
        if self.append:
            self.iteration = SearchLogger._appendCount.get(self.key, 0)

    def snapshot(self, fringe):
        """Text snapshot of a util.Stack / Queue / PriorityQueue (None when off)."""
        if not self.enabled:
            return None
        if hasattr(fringe, 'heap'):
            entries = ['%s:%s' % (_fmtState(item), priority)
                       for priority, _, item in sorted(fringe.heap)]
        else:
            entries = [_fmtState(item[0] if isinstance(item, tuple) and len(item) == 2
                                 and isinstance(item[1], list) else item)
                       for item in fringe.list]
        return '[' + ', '.join(entries) + ']'

    def expand(self, state, generated, before, fringe, h=0, f=None):
        """Record one expansion.

        generated: [(successor, action, stepCost)] that were queued this iteration.
        h defaults to 0 (uninformed searches); f defaults to g + h.
        """
        if not self.enabled:
            return
        self.iteration += 1
        parent, action = self.parents.get(state, (None, None))
        g = self.costs.get(state, 0)
        if f is None:
            f = g + h
        for successor, act, stepCost in generated:
            self.parents[successor] = (state, act)
            self.costs[successor] = g + stepCost
        self.rows.append([
            self.iteration, _fmtState(state),
            '' if parent is None else _fmtState(parent),
            '' if action is None else action,
            '[' + ', '.join('%s via %s' % (_fmtState(s), a) for s, a, _ in generated) + ']',
            before, self.snapshot(fringe),
            '[' + ', '.join(_fmtState(s) for s in self.explored) + ']',
            g, h, f])
        self.explored.append(state)

    def finish(self):
        """Write the CSV (call at every return point of a search)."""
        if not self.enabled or not self.rows:
            return
        import csv, os, time
        os.makedirs(self.dir, exist_ok=True)
        path = SearchLogger._appendFiles.get(self.key) if self.append else None
        if path is None:
            stamp = time.strftime('%Y%m%d_%H%M%S')
            path = os.path.join(self.dir, '%s_%s_%s.csv' % (self.key[0], self.key[1], stamp))
            n = 1
            while os.path.exists(path):
                path = path[:-4].rsplit('_x', 1)[0] + '_x%d.csv' % n
                n += 1
            if self.append:
                SearchLogger._appendFiles[self.key] = path
        isNew = not os.path.exists(path)
        with open(path, 'a', newline='') as fh:
            writer = csv.writer(fh)
            if isNew:
                writer.writerow(CSV_COLUMNS)
            writer.writerows(self.rows)
        if self.append:
            SearchLogger._appendCount[self.key] = self.iteration
        self.rows = []

# --- Successor ordering (Inconsistency #3) ----------------------------------
# The PDF wants North -> East -> South -> West expansion, but
# PositionSearchProblem.getSuccessors (untouchable) yields N, S, E, W and the
# autograder's pacman_1 expects that natural order.  So the reorder lives here,
# is opt-in, and is off by default.
#   * dfs / depthFirstSearch : natural order unless ENFORCE_NESW_DFS is True
#   * dfsNESW                : always N->E->S->W (use for the PDF demo)
# To revert/flip the default on demand, change ENFORCE_NESW_DFS only.
# No other algorithm uses reorderSuccessors unless a ticket explicitly calls it.
ENFORCE_NESW_DFS = False
def reorderSuccessors(successors):
    """Sort successors into N->E->S->W; non-direction actions go last and
    keep their relative order (stable sort)."""
    from game import Directions
    rank = {Directions.NORTH: 0, Directions.EAST: 1,
            Directions.SOUTH: 2, Directions.WEST: 3}
    return sorted(successors, key=lambda s: rank.get(s[1], len(rank)))

def _depthFirstSearch(problem, ordered):
    fringe = util.Stack()
    fringe.push((problem.getStartState(), []))
    explored = set()
    log = SearchLogger('dfs', problem)

    while not fringe.isEmpty():
        before = log.snapshot(fringe)
        state, actions = fringe.pop()
        if state in explored:
            continue
        if problem.isGoalState(state):
            log.expand(state, [], before, fringe)
            log.finish()
            return actions
        explored.add(state)
        successors = problem.getSuccessors(state)
        if ordered:
            # Stack is LIFO: push in reverse so North is popped/expanded first.
            successors = reorderSuccessors(successors)[::-1]
        generated = []
        for successor, action, stepCost in successors:
            if successor not in explored:
                fringe.push((successor, actions + [action]))
                generated.append((successor, action, stepCost))
        log.expand(state, generated, before, fringe)

    log.finish()
    return []

def depthFirstSearch(problem: SearchProblem):
    """
    Search the deepest nodes in the search tree first.

    Your search algorithm needs to return a list of actions that reaches the
    goal. Make sure to implement a graph search algorithm.

    To get started, you might want to try some of these simple commands to
    understand the search problem that is being passed in:

    print("Start:", problem.getStartState())
    print("Is the start a goal?", problem.isGoalState(problem.getStartState()))
    print("Start's successors:", problem.getSuccessors(problem.getStartState()))
    """
    return _depthFirstSearch(problem, ENFORCE_NESW_DFS)

def depthFirstSearchNESW(problem: SearchProblem):
    """DFS with the PDF's North -> East -> South -> West expansion order."""
    return _depthFirstSearch(problem, True)

def breadthFirstSearch(problem: SearchProblem):
    """Search the shallowest nodes in the search tree first."""
    start = problem.getStartState()
    fringe = util.Queue()
    fringe.push((start, []))
    # Every state that is in the frontier or already expanded.  Checked before
    # pushing so a state is enqueued at most once (keeps BFS optimal).
    seen = {start}
    log = SearchLogger('bfs', problem)

    while not fringe.isEmpty():
        before = log.snapshot(fringe)
        state, actions = fringe.pop()
        if problem.isGoalState(state):
            log.expand(state, [], before, fringe)
            log.finish()
            return actions
        generated = []
        for successor, action, stepCost in problem.getSuccessors(state):
            if successor not in seen:
                seen.add(successor)
                fringe.push((successor, actions + [action]))
                generated.append((successor, action, stepCost))
        log.expand(state, generated, before, fringe)

    log.finish()
    return []

def uniformCostSearch(problem: SearchProblem):
    """Search the node of least total cost first."""
    start = problem.getStartState()
    # The queue item is the bare state so PriorityQueue.update can match it and
    # lower its priority; g(n) and the path to each state live in dicts.
    fringe = util.PriorityQueue()
    fringe.push(start, 0)
    cost_so_far = {start: 0}
    paths = {start: []}
    explored = set()
    log = SearchLogger('ucs', problem)

    while not fringe.isEmpty():
        before = log.snapshot(fringe)
        state = fringe.pop()
        if problem.isGoalState(state):
            log.expand(state, [], before, fringe)
            log.finish()
            return paths[state]
        explored.add(state)
        generated = []
        for successor, action, stepCost in problem.getSuccessors(state):
            newCost = cost_so_far[state] + stepCost
            if successor not in explored and newCost < cost_so_far.get(successor, float('inf')):
                cost_so_far[successor] = newCost
                paths[successor] = paths[state] + [action]
                fringe.update(successor, newCost)
                generated.append((successor, action, stepCost))
        log.expand(state, generated, before, fringe)

    log.finish()
    return []

def nullHeuristic(state, problem=None):
    """
    A heuristic function estimates the cost from the current state to the nearest
    goal in the provided SearchProblem.  This heuristic is trivial.
    """
    return 0

def greedyBestFirstSearch(problem: SearchProblem, heuristic=nullHeuristic):
    """Search the node that looks closest to the goal (lowest h) first."""
    start = problem.getStartState()
    # Priority is h(n) alone, so a state's priority never changes: the first
    # path that reaches it is kept and it is never re-queued (no update needed).
    fringe = util.PriorityQueue()
    fringe.push(start, heuristic(start, problem))
    paths = {start: []}
    seen = {start}
    log = SearchLogger('gbfs', problem)

    while not fringe.isEmpty():
        before = log.snapshot(fringe)
        state = fringe.pop()
        # GBFS orders by h alone, so f(n) is logged as h(n).
        h = heuristic(state, problem) if log.enabled else None
        if problem.isGoalState(state):
            log.expand(state, [], before, fringe, h, h)
            log.finish()
            return paths[state]
        generated = []
        for successor, action, stepCost in problem.getSuccessors(state):
            if successor not in seen:
                seen.add(successor)
                paths[successor] = paths[state] + [action]
                fringe.push(successor, heuristic(successor, problem))
                generated.append((successor, action, stepCost))
        log.expand(state, generated, before, fringe, h, h)

    log.finish()
    return []

def aStarSearch(problem: SearchProblem, heuristic=nullHeuristic):
    """Search the node that has the lowest combined cost and heuristic first."""
    start = problem.getStartState()
    # Same shape as uniformCostSearch, but ordered by f(n) = g(n) + h(n).  The
    # item is the bare state so PriorityQueue.update can lower its priority.
    # No closed set: a state is re-opened whenever a cheaper path to it turns
    # up, which keeps A* optimal even for admissible-but-inconsistent h.
    fringe = util.PriorityQueue()
    fringe.push(start, heuristic(start, problem))
    cost_so_far = {start: 0}
    paths = {start: []}
    log = SearchLogger('astar', problem)

    while not fringe.isEmpty():
        before = log.snapshot(fringe)
        state = fringe.pop()
        h = heuristic(state, problem) if log.enabled else None
        if problem.isGoalState(state):
            log.expand(state, [], before, fringe, h)
            log.finish()
            return paths[state]
        generated = []
        for successor, action, stepCost in problem.getSuccessors(state):
            newCost = cost_so_far[state] + stepCost
            if newCost < cost_so_far.get(successor, float('inf')):
                cost_so_far[successor] = newCost
                paths[successor] = paths[state] + [action]
                fringe.update(successor, newCost + heuristic(successor, problem))
                generated.append((successor, action, stepCost))
        log.expand(state, generated, before, fringe, h)

    log.finish()
    return []


# Abbreviations
bfs = breadthFirstSearch
dfs = depthFirstSearch
dfsNESW = depthFirstSearchNESW
astar = aStarSearch
ucs = uniformCostSearch
gbfs = greedyBestFirstSearch

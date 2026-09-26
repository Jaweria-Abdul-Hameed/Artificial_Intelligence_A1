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
# effect and never changes what a search returns (an I/O failure just switches
# logging off with a warning).
#
# Rows go to evidence/<algorithm>_<layout>_<timestamp>.csv (next to search.py), one
# per state actually expanded (the goal that ends a search is not expanded).
# Logging is ON for every task-level algorithm execution, including the
# autograder and imported calls.  Set SEARCH_LOG=0 to switch it off,
# SEARCH_LOG_DIR to redirect the output folder and SEARCH_LOG_TAG to add a
# label to the file name (evidence/<algorithm>_<layout>_<tag>_<timestamp>.csv).  Internal helper
# searches (mazeDistance inside foodHeuristic, which builds its problem with
# visualize=False) are never logged.  ClosestDotSearchAgent runs one BFS per
# dot; all of them are appended to a single file per run.
CSV_COLUMNS = ['iteration', 'expanded_state', 'parent', 'action',
               'generated_successors', 'frontier_before', 'frontier_after',
               'explored', 'g', 'h', 'f']

def _loggingEnabled(problem):
    import os
    return (os.environ.get('SEARCH_LOG', '1') != '0'
            and getattr(problem, 'visualize', True))

def _layoutName():
    """Layout name from the command line (-l NAME, -lNAME, --layout NAME/=NAME),
    reduced to a filename-safe token."""
    import os, re, sys
    args = sys.argv[1:]
    # pacman.py falls back to mediumClassic when no layout is given
    name = 'mediumClassic' if os.path.basename(sys.argv[0]) == 'pacman.py' else 'unknown'
    for i, arg in enumerate(args):
        if arg in ('-l', '--layout') and i + 1 < len(args):
            name = args[i + 1]
            break
        if arg.startswith('--layout='):
            name = arg.split('=', 1)[1]
            break
        if arg.startswith('-l') and not arg.startswith('--') and len(arg) > 2:
            name = arg[2:]
            break
    name = os.path.splitext(os.path.basename(name.replace('\\', '/')))[0]
    return re.sub(r'[^A-Za-z0-9._-]', '-', name) or 'unknown'

def _fmtState(state):
    """Compact text for a state; food grids are shown as (position, dots left)."""
    if (isinstance(state, tuple) and len(state) == 2
            and hasattr(state[1], 'count') and hasattr(state[1], 'asList')):
        return '(%s, food=%d)' % (state[0], state[1].count())
    return str(state)

class SearchLogger:
    """Writes one CSV row per expanded state, as the search runs."""
    _appendFiles = {}   # (algorithm, layout) -> path, for repeated sub-searches
    _appendCount = {}   # (algorithm, layout) -> iterations already written there

    def __init__(self, algorithm, problem):
        self.enabled = _loggingEnabled(problem)
        self.append = False
        self.file = None
        self.writer = None
        if not self.enabled:
            return
        import os
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
        """Text snapshot of a util.Stack / Queue / PriorityQueue, next state to be
        expanded first (None when logging is off)."""
        if not self.enabled:
            return None
        if hasattr(fringe, 'heap'):
            entries = ['%s:%s' % (_fmtState(item), priority)
                       for priority, _, item in sorted(fringe.heap)]
        else:
            # Stack / Queue items are (state, actions) pairs
            # util.Stack and util.Queue both pop from the end of .list
            entries = [_fmtState(item[0]) for item in reversed(fringe.list)]
        return '[' + ', '.join(entries) + ']'

    def _open(self):
        """Create (or reopen) the CSV and write the header when the file is new."""
        import csv, os, re, time
        os.makedirs(self.dir, exist_ok=True)
        path = SearchLogger._appendFiles.get(self.key) if self.append else None
        if path is None:
            tag = re.sub(r'[^A-Za-z0-9._-]', '-', os.environ.get('SEARCH_LOG_TAG', ''))
            stem = '_'.join(filter(None, [self.key[0], self.key[1], tag,
                                         time.strftime('%Y%m%d_%H%M%S')]))
            path = os.path.join(self.dir, stem + '.csv')
            n = 1
            while os.path.exists(path):
                path = os.path.join(self.dir, '%s_%d.csv' % (stem, n))
                n += 1
            if self.append:
                SearchLogger._appendFiles[self.key] = path
        isNew = not os.path.exists(path)
        self.file = open(path, 'a', newline='', encoding='utf-8')
        self.writer = csv.writer(self.file)
        if isNew:
            self.writer.writerow(CSV_COLUMNS)

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
        row = [
            self.iteration, _fmtState(state),
            '' if parent is None else _fmtState(parent),
            '' if action is None else action,
            '[' + ', '.join('%s via %s' % (_fmtState(s), a) for s, a, _ in generated) + ']',
            before, self.snapshot(fringe),
            '[' + ', '.join(_fmtState(s) for s in self.explored) + ']',
            g, h, f]
        self.explored.append(state)
        try:
            if self.file is None:
                self._open()
            self.writer.writerow(row)
        except Exception as err:   # logging must never break a search
            print('[search] CSV logging disabled: %s' % err)
            self.enabled = False

    def finish(self):
        """Close the CSV (call at every return point of a search)."""
        if self.enabled and self.file is None:
            # Nothing was expanded (start state is the goal): leave a header-only trace.
            try:
                self._open()
            except Exception as err:   # logging must never break a search
                print('[search] CSV logging disabled: %s' % err)
                self.enabled = False
        if self.append:
            SearchLogger._appendCount[self.key] = self.iteration
        if self.file is None:
            return
        try:
            self.file.close()
        except OSError:
            pass
        self.file = None


def depthFirstSearch(problem: SearchProblem):
    """
    Search the deepest nodes in the search tree first.

    Graph-search DFS with a LIFO util.Stack as the fringe and an explicit
    explored set.  Successors are pushed in the order problem.getSuccessors
    returns them (North, South, East, West for the Pacman problems), which is
    the order the autograder's reference solutions were generated with.
    """
    frontierStack = util.Stack()
    frontierStack.push((problem.getStartState(), []))
    statesAlreadyExplored = set()
    executionTraceLogger = SearchLogger('dfs', problem)

    while not frontierStack.isEmpty():
        frontierBeforeRemoval = executionTraceLogger.snapshot(frontierStack)
        currentSearchState, pathActionsSoFar = frontierStack.pop()
        if currentSearchState in statesAlreadyExplored:
            continue
        if problem.isGoalState(currentSearchState):
            # The goal is selected, not expanded: getSuccessors is never called on it,
            # so it gets no row and the row count equals 'Search nodes expanded'.
            executionTraceLogger.finish()
            return pathActionsSoFar
        statesAlreadyExplored.add(currentSearchState)
        generatedSuccessorTriples = []
        for successorState, successorAction, successorStepCost in problem.getSuccessors(currentSearchState):
            if successorState not in statesAlreadyExplored:
                frontierStack.push(
                    (successorState, pathActionsSoFar + [successorAction]))
                generatedSuccessorTriples.append(
                    (successorState, successorAction, successorStepCost))
        executionTraceLogger.expand(
            currentSearchState, generatedSuccessorTriples,
            frontierBeforeRemoval, frontierStack)

    executionTraceLogger.finish()
    return []

def breadthFirstSearch(problem: SearchProblem):
    """Search the shallowest nodes in the search tree first."""
    initialSearchState = problem.getStartState()
    frontierQueue = util.Queue()
    frontierQueue.push((initialSearchState, []))
    # Every state that is in the frontier or already expanded.  Checked before
    # pushing so a state is enqueued at most once (keeps BFS optimal).
    statesAlreadyDiscovered = {initialSearchState}
    executionTraceLogger = SearchLogger('bfs', problem)

    while not frontierQueue.isEmpty():
        frontierBeforeRemoval = executionTraceLogger.snapshot(frontierQueue)
        currentSearchState, pathActionsSoFar = frontierQueue.pop()
        if problem.isGoalState(currentSearchState):
            # The goal is selected, not expanded, so it gets no CSV row.
            executionTraceLogger.finish()
            return pathActionsSoFar
        generatedSuccessorTriples = []
        for successorState, successorAction, successorStepCost in problem.getSuccessors(currentSearchState):
            if successorState not in statesAlreadyDiscovered:
                statesAlreadyDiscovered.add(successorState)
                frontierQueue.push(
                    (successorState, pathActionsSoFar + [successorAction]))
                generatedSuccessorTriples.append(
                    (successorState, successorAction, successorStepCost))
        executionTraceLogger.expand(
            currentSearchState, generatedSuccessorTriples,
            frontierBeforeRemoval, frontierQueue)

    executionTraceLogger.finish()
    return []

def uniformCostSearch(problem: SearchProblem):
    """Search the node of least total cost first."""
    initialSearchState = problem.getStartState()
    # The queue item is the bare state so PriorityQueue.update can match it and
    # lower its priority; g(n) and the path to each state live in dicts.
    costPriorityFrontier = util.PriorityQueue()
    costPriorityFrontier.push(initialSearchState, 0)
    cheapestCostFound = {initialSearchState: 0}
    actionPathsByState = {initialSearchState: []}
    statesWithFinalCost = set()
    executionTraceLogger = SearchLogger('ucs', problem)

    while not costPriorityFrontier.isEmpty():
        frontierBeforeRemoval = executionTraceLogger.snapshot(costPriorityFrontier)
        currentSearchState = costPriorityFrontier.pop()
        if problem.isGoalState(currentSearchState):
            # The goal is selected, not expanded, so it gets no CSV row.
            executionTraceLogger.finish()
            return actionPathsByState[currentSearchState]
        statesWithFinalCost.add(currentSearchState)
        generatedSuccessorTriples = []
        for successorState, successorAction, successorStepCost in problem.getSuccessors(currentSearchState):
            candidatePathCost = (cheapestCostFound[currentSearchState]
                                 + successorStepCost)
            if (successorState not in statesWithFinalCost
                    and candidatePathCost < cheapestCostFound.get(
                        successorState, float('inf'))):
                cheapestCostFound[successorState] = candidatePathCost
                actionPathsByState[successorState] = (
                    actionPathsByState[currentSearchState] + [successorAction])
                costPriorityFrontier.update(successorState, candidatePathCost)
                generatedSuccessorTriples.append(
                    (successorState, successorAction, successorStepCost))
        executionTraceLogger.expand(
            currentSearchState, generatedSuccessorTriples,
            frontierBeforeRemoval, costPriorityFrontier)

    executionTraceLogger.finish()
    return []

def nullHeuristic(state, problem=None):
    """
    A heuristic function estimates the cost from the current state to the nearest
    goal in the provided SearchProblem.  This heuristic is trivial.
    """
    return 0

def greedyBestFirstSearch(problem: SearchProblem, heuristic=nullHeuristic):
    """Search the node that looks closest to the goal (lowest h) first."""
    initialSearchState = problem.getStartState()
    # Priority is h(n) alone, so a state's priority never changes: the first
    # path that reaches it is kept and it is never re-queued (no update needed).
    heuristicPriorityFrontier = util.PriorityQueue()
    heuristicValuesByState = {
        initialSearchState: heuristic(initialSearchState, problem)}
    heuristicPriorityFrontier.push(
        initialSearchState, heuristicValuesByState[initialSearchState])
    actionPathsByState = {initialSearchState: []}
    statesAlreadyDiscovered = {initialSearchState}
    executionTraceLogger = SearchLogger('gbfs', problem)

    while not heuristicPriorityFrontier.isEmpty():
        frontierBeforeRemoval = executionTraceLogger.snapshot(
            heuristicPriorityFrontier)
        currentSearchState = heuristicPriorityFrontier.pop()
        # GBFS orders by h alone, so f(n) is logged as h(n).
        currentHeuristicValue = heuristicValuesByState[currentSearchState]
        if problem.isGoalState(currentSearchState):
            # The goal is selected, not expanded, so it gets no CSV row.
            executionTraceLogger.finish()
            return actionPathsByState[currentSearchState]
        generatedSuccessorTriples = []
        for successorState, successorAction, successorStepCost in problem.getSuccessors(currentSearchState):
            if successorState not in statesAlreadyDiscovered:
                statesAlreadyDiscovered.add(successorState)
                actionPathsByState[successorState] = (
                    actionPathsByState[currentSearchState] + [successorAction])
                heuristicValuesByState[successorState] = heuristic(
                    successorState, problem)
                heuristicPriorityFrontier.push(
                    successorState, heuristicValuesByState[successorState])
                generatedSuccessorTriples.append(
                    (successorState, successorAction, successorStepCost))
        executionTraceLogger.expand(
            currentSearchState, generatedSuccessorTriples,
            frontierBeforeRemoval, heuristicPriorityFrontier,
            currentHeuristicValue, currentHeuristicValue)

    executionTraceLogger.finish()
    return []

def aStarSearch(problem: SearchProblem, heuristic=nullHeuristic):
    """Search the node that has the lowest combined cost and heuristic first."""
    initialSearchState = problem.getStartState()
    # Same shape as uniformCostSearch, but ordered by f(n) = g(n) + h(n).  The
    # item is the bare state so PriorityQueue.update can lower its priority.
    # No closed set: a state is re-opened whenever a cheaper path to it turns
    # up, which keeps A* optimal even for admissible-but-inconsistent h.
    evaluationPriorityFrontier = util.PriorityQueue()
    heuristicValuesByState = {
        initialSearchState: heuristic(initialSearchState, problem)}
    evaluationPriorityFrontier.push(
        initialSearchState, heuristicValuesByState[initialSearchState])
    cheapestCostFound = {initialSearchState: 0}
    actionPathsByState = {initialSearchState: []}
    executionTraceLogger = SearchLogger('astar', problem)

    while not evaluationPriorityFrontier.isEmpty():
        frontierBeforeRemoval = executionTraceLogger.snapshot(
            evaluationPriorityFrontier)
        currentSearchState = evaluationPriorityFrontier.pop()
        currentHeuristicValue = heuristicValuesByState[currentSearchState]
        if problem.isGoalState(currentSearchState):
            # The goal is selected, not expanded, so it gets no CSV row.
            executionTraceLogger.finish()
            return actionPathsByState[currentSearchState]
        generatedSuccessorTriples = []
        for successorState, successorAction, successorStepCost in problem.getSuccessors(currentSearchState):
            candidatePathCost = (cheapestCostFound[currentSearchState]
                                 + successorStepCost)
            if candidatePathCost < cheapestCostFound.get(
                    successorState, float('inf')):
                cheapestCostFound[successorState] = candidatePathCost
                actionPathsByState[successorState] = (
                    actionPathsByState[currentSearchState] + [successorAction])
                if successorState not in heuristicValuesByState:
                    heuristicValuesByState[successorState] = heuristic(
                        successorState, problem)
                evaluationPriorityFrontier.update(
                    successorState,
                    candidatePathCost + heuristicValuesByState[successorState])
                generatedSuccessorTriples.append(
                    (successorState, successorAction, successorStepCost))
        executionTraceLogger.expand(
            currentSearchState, generatedSuccessorTriples,
            frontierBeforeRemoval, evaluationPriorityFrontier,
            currentHeuristicValue)

    executionTraceLogger.finish()
    return []


# Abbreviations
bfs = breadthFirstSearch
dfs = depthFirstSearch
astar = aStarSearch
ucs = uniformCostSearch
gbfs = greedyBestFirstSearch

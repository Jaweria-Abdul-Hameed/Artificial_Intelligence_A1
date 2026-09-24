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

    while not fringe.isEmpty():
        state, actions = fringe.pop()
        if state in explored:
            continue
        if problem.isGoalState(state):
            return actions
        explored.add(state)
        successors = problem.getSuccessors(state)
        if ordered:
            # Stack is LIFO: push in reverse so North is popped/expanded first.
            successors = reorderSuccessors(successors)[::-1]
        for successor, action, _ in successors:
            if successor not in explored:
                fringe.push((successor, actions + [action]))

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

    while not fringe.isEmpty():
        state, actions = fringe.pop()
        if problem.isGoalState(state):
            return actions
        for successor, action, _ in problem.getSuccessors(state):
            if successor not in seen:
                seen.add(successor)
                fringe.push((successor, actions + [action]))

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

    while not fringe.isEmpty():
        state = fringe.pop()
        if problem.isGoalState(state):
            return paths[state]
        explored.add(state)
        for successor, action, stepCost in problem.getSuccessors(state):
            newCost = cost_so_far[state] + stepCost
            if successor not in explored and newCost < cost_so_far.get(successor, float('inf')):
                cost_so_far[successor] = newCost
                paths[successor] = paths[state] + [action]
                fringe.update(successor, newCost)

    return []

def nullHeuristic(state, problem=None):
    """
    A heuristic function estimates the cost from the current state to the nearest
    goal in the provided SearchProblem.  This heuristic is trivial.
    """
    return 0

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

    while not fringe.isEmpty():
        state = fringe.pop()
        if problem.isGoalState(state):
            return paths[state]
        for successor, action, stepCost in problem.getSuccessors(state):
            newCost = cost_so_far[state] + stepCost
            if newCost < cost_so_far.get(successor, float('inf')):
                cost_so_far[successor] = newCost
                paths[successor] = paths[state] + [action]
                fringe.update(successor, newCost + heuristic(successor, problem))

    return []


# Abbreviations
bfs = breadthFirstSearch
dfs = depthFirstSearch
dfsNESW = depthFirstSearchNESW
astar = aStarSearch
ucs = uniformCostSearch

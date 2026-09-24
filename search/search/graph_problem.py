"""Tiny explicit-graph SearchProblem shared by the test files."""
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

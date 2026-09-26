AI2002 - Artificial Intelligence - Assignment 01 (Pacman Search)
=================================================================

GROUP MEMBERS
  Jaweria Abdul Hameed   24i-3025
  Mohsin Khan            24i-3135

ENVIRONMENT
  Python        3.14.7 (any Python 3.7+ works; no third-party packages needed)
  OS            Windows 11 Home (10.0.26200)
  Hardware      Intel Core 9 270H (14 cores / 20 threads), 15.6 GB RAM
  Display       Tk graphics (standard with Python); add -q to any command to run
                without a window.

WHAT WAS EDITED / ADDED
  search.py         DFS, BFS, UCS, GBFS, A* and the shared CSV trace logger
  searchAgents.py   CornersProblem, cornersHeuristic, foodHeuristic,
                    AnyFoodSearchProblem, ClosestDotSearchAgent
  layouts/24i3025Search.lay   original custom maze (Section 4)
  evidence/         CSV trace of every run + screenshots/ (Section 3 and 5)
  report.pdf        analysis report
  Every other starter file (pacman.py, game.py, util.py, layout.py,
  graphicsDisplay.py, graphicsUtils.py, textDisplay.py, ...) is unmodified.

  Every algorithm is written directly inside its own provided function, with no
  helper delegation, and expands successors in the order getSuccessors returns them.

RUN COMMANDS  (run from this folder)
  Task 1  DFS
    python pacman.py -l tinyMaze -p SearchAgent -a fn=dfs
    python pacman.py -l mediumMaze -p SearchAgent -a fn=dfs
    python pacman.py -l bigMaze -z .5 -p SearchAgent -a fn=dfs
  Task 2  BFS
    python pacman.py -l mediumMaze -p SearchAgent -a fn=bfs
    python pacman.py -l bigMaze -z .5 -p SearchAgent -a fn=bfs
  Task 3  UCS
    python pacman.py -l mediumMaze -p SearchAgent -a fn=ucs
    python pacman.py -l mediumDenselyMaze -p SearchAgent -a fn=ucs
    python pacman.py -l stayEastSearch -p SearchAgent -a fn=ucs
    python pacman.py -l mediumMaze -p SearchAgent -a fn=ucs -z .5
    python pacman.py -l mediumMaze -p StayEastSearchAgent
  Task 4  GBFS
    python pacman.py -l bigMaze -z .5 -p SearchAgent -a fn=gbfs,heuristic=manhattanHeuristic
    python pacman.py -l bigMaze -z .5 -p SearchAgent -a fn=gbfs,heuristic=euclideanHeuristic
  Task 5  A*
    python pacman.py -l bigMaze -z .5 -p SearchAgent -a fn=astar,heuristic=nullHeuristic
    python pacman.py -l bigMaze -z .5 -p SearchAgent -a fn=astar,heuristic=manhattanHeuristic
  Task 6  Corners
    python pacman.py -l tinyCorners -p SearchAgent -a fn=bfs,prob=CornersProblem
    python pacman.py -l mediumCorners -p AStarCornersAgent -z .5
  Task 7  Food
    python pacman.py -l trickySearch -p AStarFoodSearchAgent
    python pacman.py -l bigSearch -p ClosestDotSearchAgent
  Custom maze (Section 4), all five algorithms
    python pacman.py -l 24i3025Search -p SearchAgent -a fn=dfs
    python pacman.py -l 24i3025Search -p SearchAgent -a fn=bfs
    python pacman.py -l 24i3025Search -p SearchAgent -a fn=ucs
    python pacman.py -l 24i3025Search -p SearchAgent -a fn=gbfs,heuristic=manhattanHeuristic
    python pacman.py -l 24i3025Search -p SearchAgent -a fn=astar,heuristic=manhattanHeuristic
  Autograder
    python autograder.py                 (all of q1-q8)
    python autograder.py -q q7           (a single question)
    python autograder.py --no-graphics

CSV TRACE LOGGING
  Every task-level algorithm execution writes evidence/<algorithm>_<layout>_<timestamp>.csv
  with the columns:
    iteration, expanded_state, parent, action, generated_successors,
    frontier_before, frontier_after, explored, g, h, f
  One row per expanded state (the goal that ends a search is selected, not
  expanded, so the row count equals "Search nodes expanded").  For DFS, BFS and
  UCS h = 0 and f = g so every file has the same schema; GBFS logs f = h (it
  orders by h alone).  Logging
  is on under pacman.py, the autograder, and imported task calls. Set
  SEARCH_LOG=0 to switch it off, SEARCH_LOG_DIR=<folder> to redirect it, or
  SEARCH_LOG_TAG=<label> to insert a label into the file name.
  The explored column lists every state expanded so far, so a file grows with the
  square of the run length (mediumCorners is about 6.6 MB).
  ClosestDotSearchAgent runs one BFS per dot; all of them are appended to a
  single CSV (iteration keeps counting up across the sub-searches).

NOTES ON PDF vs. STARTER-CODE DISCREPANCIES (all handled without editing any forbidden file)
  1. Section 3 needs CSV logging but pacman.py/util.py etc. are read-only, so the
     logger lives entirely in search.py.
  2. There is no GBFS stub or autograder question in the starter code.  gbfs /
     greedyBestFirstSearch was added to search.py (SearchAgent finds it via getattr).
  3. Task 1 names the order N,E,S,W, but PositionSearchProblem.getSuccessors
     (untouchable) returns N,S,E,W and the autograder q1 reference solutions
     are generated from that order. Per the teacher, all tests must pass, so
     depthFirstSearch pushes successors in the order getSuccessors returns them.
     No other algorithm reorders successors.
  4. Two UCS example commands reference layouts that the starter code does not
     ship (mediumDenselyMaze, stayEastSearch).  Both were created in layouts/, so
     the PDF commands run as written.  "-l mediumMaze -p StayEastSearchAgent" is kept too.
  5. The custom layout is named 24i3025Search.lay (Section 4 / Section 5 naming);
     Step 2 of the PDF says just "Search.lay".
  6. DFS/BFS/UCS have no heuristic, so their CSV rows use h = 0, f = g.
  7. Two-person group: the layout is named after the first member's ID.

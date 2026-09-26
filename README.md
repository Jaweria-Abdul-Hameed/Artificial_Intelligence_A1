# Pacman Search Project

**AI2002 – Artificial Intelligence · Assignment 01 · Deadline 27 September 2026 · 150 marks**

| Team member | Roll no. |
|:---|:---|
| Jaweria Abdul Hameed | 24i-3025 |
| Mohsin Khan | 24i-3135 |

Five search algorithms, two multi-goal problems, an automatic CSV trace for every run, and a custom maze built to fool greedy search, all on the UC Berkeley Pacman framework.

**Status:** implementation follows the PDF literally and leaves all protected code untouched. The supplied q1 path fixture expects the starter's N-S-E-W successor order, while the PDF mandates N-E-S-W for DFS; this mismatch is documented rather than hidden.

---

## What was built

| Task | Where | Notes |
|:---|:---|:---|
| **DFS** | `search.py` | LIFO `util.Stack`, explicit explored set. Successors are expanded in the order `getSuccessors` returns them (N, S, E, W), which the autograder q1 reference solutions require. |
| **BFS** | `search.py` | FIFO `util.Queue`; a state is enqueued at most once, so paths are shortest on unit costs. |
| **UCS** | `search.py` | `util.PriorityQueue` ordered by g(n); `update` lowers the priority of a state already on the fringe. |
| **GBFS** | `search.py` | Ordered by h(n) only; `gbfs` / `greedyBestFirstSearch`; heuristic passed on the command line. |
| **A\*** | `search.py` | f(n) = g(n) + h(n); re-opens a state when a cheaper path appears. |
| **CSV logger** | `search.py` | One shared `SearchLogger`, called from inside each algorithm's own loop. |
| **CornersProblem** | `searchAgents.py` | State is `(position, visited corners)`, corners kept in a fixed order so equal sets are equal states. |
| **cornersHeuristic** | `searchAgents.py` | Exact shortest Manhattan tour over the unvisited corners. Admissible and consistent. |
| **foodHeuristic** | `searchAgents.py` | Nearest dot + minimum spanning tree over the remaining dots, using true maze distances (cached). Admissible and consistent. |
| **AnyFoodSearchProblem / ClosestDotSearchAgent** | `searchAgents.py` | Goal test is "standing on food"; BFS finds the nearest dot. |
| **Custom maze** | `layouts/24i3025Search.lay` | Branches, dead ends and a serpentine decoy; GBFS returns 47 steps, A\* returns 37. |

Every algorithm is written directly inside its own provided function. The one exception is `depthFirstSearch`, which delegates to `_depthFirstSearch` to enforce the mandatory N-E-S-W order.

Only `search.py`, `searchAgents.py` and the new layout were edited. `pacman.py`, `game.py`, `util.py`, `layout.py`, `graphicsDisplay.py`, `graphicsUtils.py` and `textDisplay.py` are byte-identical to the starter code, the `SearchAgent`, `PositionSearchProblem` and `FoodSearchProblem` classes are unchanged, and all 7 `# DO NOT CHANGE` lines are intact.

---

## Results

Path cost and nodes expanded, straight from the run output and cross-checked against each CSV.

| Run | Cost | Nodes |
|:---|---:|---:|
| DFS tinyMaze / mediumMaze / bigMaze | 8 / 244 / 210 | 15 / 267 / 519 |
| DFS alias N-E-S-W mediumMaze | 244 | 267 |
| BFS mediumMaze / bigMaze | 68 / 210 | 269 / 620 |
| UCS mediumMaze | 68 | 269 |
| GBFS bigMaze (Manhattan / Euclidean) | 210 / 210 | 466 / 471 |
| A\* bigMaze (null / Manhattan) | 210 / 210 | 620 / 549 |
| BFS tinyCorners | 28 | 252 |
| A\* mediumCorners | 106 | 741 |
| A\* trickySearch | 60 | 255 |
| ClosestDot bigSearch | 350 | one BFS per dot |

**The greedy trap** (`24i3025Search`): DFS 37 steps (97 nodes), BFS 37, UCS 37, **GBFS 47** (54 nodes), **A\* 37** (84 nodes). Greedy search expands fewer nodes but commits to a long serpentine that looks close to the goal in Manhattan distance; A\* adds the cost already paid and takes the shorter route.

---

## Repository layout

```
.
├── search/search/                 # the project folder that gets zipped
│   ├── search.py                  # EDITED: DFS, BFS, UCS, GBFS, A*, CSV logger
│   ├── searchAgents.py            # EDITED: corners, food heuristic, closest dot
│   ├── layouts/24i3025Search.lay  # ADDED: custom maze
│   ├── evidence/                  # ADDED: experiment/autograder CSV traces + 22 screenshots
│   ├── README.txt                 # ADDED: submission README (specs, commands)
│   ├── report.pdf                 # ADDED: 7-page report
│   ├── pacman.py game.py util.py layout.py
│   │   graphicsDisplay.py graphicsUtils.py textDisplay.py   # untouched
│   ├── autograder.py, test_cases/ # starter test harness (q1-q8)
│   └── test_*.py, graph_problem.py# our own tests (kept out of the ZIP)
├── tools/                         # helper scripts, not part of the submission
│   ├── run_experiments.py         # reruns every command: CSVs, screenshots, results.json
│   ├── snap.py                    # screenshot of a finished game
│   ├── build_report.py           # results.json + screenshots -> report.pdf
│   ├── build_dashboard.py         # -> interactive results explorer (dashboard.html)
│   └── make_zip.py                # builds and verifies SearchProject.zip
├── docs/                          # agent and issue-tracker notes
├── tickets.md                     # original ticket backlog and PDF/code discrepancies
└── Assignment 01.pdf              # the assignment
```

---

## Running it

Python 3.7+ with Tk (bundled with Python). No third-party packages are needed for the project itself; the helper scripts in `tools/` also use Pillow, and `build_report.py` needs Edge or Chrome. Run everything below from `search/search`.

```bash
cd search/search
python pacman.py                    # sanity check
python autograder.py                # all of q1-q8
python autograder.py -q q7          # one question
```

| Task | Commands |
|:---|:---|
| 1 DFS | `python pacman.py -l tinyMaze -p SearchAgent -a fn=dfs`<br>`python pacman.py -l mediumMaze -p SearchAgent -a fn=dfs`<br>`python pacman.py -l bigMaze -z .5 -p SearchAgent -a fn=dfs` |
| 2 BFS | `python pacman.py -l mediumMaze -p SearchAgent -a fn=bfs`<br>`python pacman.py -l bigMaze -z .5 -p SearchAgent -a fn=bfs` |
| 3 UCS | `python pacman.py -l mediumMaze -p SearchAgent -a fn=ucs`<br>`python pacman.py -l mediumMaze -p SearchAgent -a fn=ucs -z .5`<br>`python pacman.py -l mediumMaze -p StayEastSearchAgent` |
| 4 GBFS | `python pacman.py -l bigMaze -z .5 -p SearchAgent -a fn=gbfs,heuristic=manhattanHeuristic`<br>`python pacman.py -l bigMaze -z .5 -p SearchAgent -a fn=gbfs,heuristic=euclideanHeuristic` |
| 5 A\* | `python pacman.py -l bigMaze -z .5 -p SearchAgent -a fn=astar,heuristic=nullHeuristic`<br>`python pacman.py -l bigMaze -z .5 -p SearchAgent -a fn=astar,heuristic=manhattanHeuristic` |
| 6 Corners | `python pacman.py -l tinyCorners -p SearchAgent -a fn=bfs,prob=CornersProblem`<br>`python pacman.py -l mediumCorners -p AStarCornersAgent -z .5` |
| 7 Food | `python pacman.py -l trickySearch -p AStarFoodSearchAgent`<br>`python pacman.py -l bigSearch -p ClosestDotSearchAgent` |
| Custom maze | `python pacman.py -l 24i3025Search -p SearchAgent -a fn=<dfs\|bfs\|ucs>`<br>`... -a fn=gbfs,heuristic=manhattanHeuristic`<br>`... -a fn=astar,heuristic=manhattanHeuristic` |

Add `-q` to any command to run without a window.

### CSV traces

Every task-level execution writes `evidence/<algorithm>_<layout>[_<tag>]_<timestamp>.csv` with the columns

`iteration, expanded_state, parent, action, generated_successors, frontier_before, frontier_after, explored, g, h, f`

One row per expanded state (plus the goal row). DFS, BFS and UCS log `h = 0`, `f = g` so every file has the same schema; GBFS logs `f = h`. Logging is on for `pacman.py`, autograder, and imported task calls. `SEARCH_LOG=0` explicitly disables it, `SEARCH_LOG_DIR` redirects the folder, and `SEARCH_LOG_TAG` adds a label. Internal `visualize=False` helper searches remain suppressed so `mazeDistance` does not recursively flood the evidence directory.

### Regenerating the evidence

From the repo root:

```bash
python tools/run_experiments.py     # CSVs, screenshots, tools/results.json, autograder score
python tools/build_report.py        # search/search/report.pdf
python tools/build_dashboard.py     # tools/dashboard.html
python tools/make_zip.py            # SearchProject.zip + checks
```

---

## Where the PDF and the starter code disagree

Handled without editing any forbidden file. Full detail is in `tickets.md` section 0, `search/search/README.txt` and the report appendix.

1. **CSV logging vs. forbidden files.** The logger lives in `search.py`, so no forbidden file changes.
2. **GBFS has no stub and no autograder question.** `gbfs` / `greedyBestFirstSearch` was added to `search.py`; `SearchAgent` finds it with `getattr`. It is covered by our own tests instead.
3. **N-E-S-W order.** Task 1 names N, E, S, W, but `PositionSearchProblem.getSuccessors` (untouchable) returns N, S, E, W and the q1 reference solutions are generated from it. Per the teacher, all autograder tests must pass, so `depthFirstSearch` uses the `getSuccessors` order (no reordering). No other algorithm reorders successors.
4. **Two UCS commands cannot run.** `mediumDenselyMaze` and `stayEastSearch` are not layouts. Substitutes: `-l mediumMaze ... fn=ucs -z .5` and `-l mediumMaze -p StayEastSearchAgent`.
5. **Layout name.** Step 2 says `Search.lay`, Section 4 says `[YourID]Search.lay`; we use `24i3025Search.lay`. The goal sits at (1, 1) because `SearchAgent` uses that default goal.
6. **CSV schema for uninformed search.** `h = 0`, `f = g` so all files share the same columns.
7. **Two-person group.** Both members are named in the READMEs and the report; the layout uses the first ID.
8. **Protected code.** The 7 `# DO NOT CHANGE` lines and the three protected classes are unchanged.

---

## Submission package

`python tools/make_zip.py` builds `SearchProject.zip` (kept out of git) with a single `SearchProject/` folder that matches the PDF's Section 5 layout: the starter code, the edited `search.py` and `searchAgents.py`, `layouts/` with the custom maze, `README.txt`, `report.pdf`, and `evidence/` with all CSVs and screenshots. Our own test files are left out. The script unzips the result, checks exclusions and byte-identical protected files, and records the clean-extraction autograder result.

## Rubric (150 marks)

| Category | Marks | Where it is covered |
|:---|---:|:---|
| Automated test execution | 20 | `python autograder.py` |
| Live demonstration / viva | 20 | commands above, `search/search/README.txt` |
| A\*, UCS, DFS, BFS, GBFS (10 each) | 50 | `search.py` |
| Heuristic design and analysis | 10 | report section 3 |
| Multi-goal search tasks | 10 | `searchAgents.py`, report section 2 |
| Automatic CSV trace logging | 10 | `SearchLogger`, `evidence/` |
| Custom maze and experiments | 10 | `layouts/24i3025Search.lay`, report sections 4 and 5 |
| Report and complexity analysis | 10 | `report.pdf` |
| Code quality and style | 10 | comments, interface rules kept |

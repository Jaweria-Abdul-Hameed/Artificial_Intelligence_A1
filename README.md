# Pacman Search Project (Artificial Intelligence — Assignment 01)

**Course:** AI2002 – Artificial Intelligence  
**Deadline:** 27th September 2026  
**Total Marks:** 150 Marks  
**Team Members:**
- **Jaweria Abdul Hameed** (Roll No: `24i-3025`)
- **Group Partner** (Roll No: `24i-3135`)

---

## 📖 Project Overview

This repository contains the implementation of search algorithms for the UC Berkeley Pacman AI framework for **AI2002: Assignment 01**. Pacman navigates through various mazes and food environments to find paths to goals using both uninformed and informed search techniques, multi-goal state space formulations, heuristic design, and automated execution logging.

### Key Capabilities & Objectives
1. **Uninformed Search:**
   - **Depth-First Search (DFS):** Graph search utilizing a LIFO Stack from `util.py`.
   - **Breadth-First Search (BFS):** Graph search utilizing a FIFO Queue from `util.py` guaranteeing optimal path length on unweighted graphs.
2. **Informed Search:**
   - **Uniform-Cost Search (UCS):** Priority Queue ordered by path cost $g(n)$, with frontier re-prioritization (`update`).
   - **Greedy Best-First Search (GBFS):** Priority Queue ordered strictly by heuristic $h(n)$ with dynamic CLI parameter passing.
   - **A* Search:** Priority Queue ordered by $f(n) = g(n) + h(n)$ verifying path optimality with consistent heuristics.
3. **Multi-Goal State Spaces & Custom Heuristics:**
   - **Corners Problem (`CornersProblem`):** State representation as `(position, tuple_of_visited_corners)` to visit all four maze corners.
   - **Corners Heuristic (`cornersHeuristic`):** Mathematically admissible and consistent heuristic.
   - **Eating All Food Dots (`FoodSearchProblem` & `foodHeuristic`):** Minimum Spanning Tree (MST) / bottleneck heuristic to optimize expansions on `trickySearch`.
   - **Nearest Food Dot (`AnyFoodSearchProblem` & `ClosestDotSearchAgent`):** Fast dot collection using BFS.
4. **Automated CSV Trace Logging:**
   - Step-by-step state expansion logging directly to CSV files inside `evidence/`.
5. **Custom Maze Design & Analysis:**
   - Custom layout `layouts/24i3025Search.lay` featuring decision branches, dead ends, and deceptive heuristic traps contrasting GBFS and A*.

---

## 📁 Repository Structure & File Rules

Following strict assignment instructions, we only write code where required (`"*** YOUR CODE HERE ***"` markers) and never modify core engine files.

```
.
├── search/search/
│   ├── search.py                  # PRIMARY EDITABLE: DFS, BFS, UCS, GBFS, A*, CSV Logger
│   ├── searchAgents.py            # SECONDARY EDITABLE: CornersProblem, food heuristics, ClosestDot
│   ├── pacman.py                  # SYSTEM CORE - DO NOT MODIFY
│   ├── game.py                    # SYSTEM CORE - DO NOT MODIFY
│   ├── util.py                    # SYSTEM CORE - DO NOT MODIFY (Stack, Queue, PriorityQueue)
│   ├── layout.py                  # SYSTEM CORE - DO NOT MODIFY
│   ├── graphicsDisplay.py         # SYSTEM CORE - DO NOT MODIFY
│   ├── graphicsUtils.py           # SYSTEM CORE - DO NOT MODIFY
│   ├── textDisplay.py             # SYSTEM CORE - DO NOT MODIFY
│   ├── autograder.py              # Automated test harness (q1-q8)
│   ├── layouts/                   # Standard mazes + custom 24i3025Search.lay
│   └── test_cases/                # Question test configurations (q1-q8)
├── evidence/                      # Execution CSV trace logs & screenshots
├── tickets.md                     # Complete project ticket backlog (AI-00 to AI-13)
├── Assignment 01.pdf              # Official assignment specification
└── README.md                      # Project documentation and guide
```

---

## ⚠️ Codebase Inconsistencies & Resolutions (Read First)

As documented in `tickets.md` Section 0, cross-referencing `Assignment 01.pdf` with the starter code revealed 8 specific discrepancies:

1. **Forbidden Files vs. CSV Logging:**  
   CSV logging is implemented entirely inside `search.py` using Python's standard library `csv` module, preserving all forbidden files untouched.
2. **Task 4 (GBFS) Missing in Starter Code:**  
   `search.py` did not contain a `greedyBestFirstSearch` stub or `gbfs` alias, and `autograder.py` contains no test for GBFS. We implement `greedyBestFirstSearch` in `search.py` and verify it manually against A*.
3. **DFS Successor Order vs. Autograder:**  
   The PDF mentions North → East → South → West expansion order. However, the standard autograder (`q1`) expects the natural order returned by `PositionSearchProblem` (`[North, South, East, West]`). Forcing reordering breaks `q1/pacman_1.test`. DFS uses the natural order for standard autograder compatibility.
4. **Nonexistent UCS Layouts in PDF:**  
   The PDF references `mediumDenselyMaze` (nonexistent) and `stayEastSearch` (an agent class, not a layout). Working substitutes: `python pacman.py -l mediumMaze -p StayEastSearchAgent` and `python pacman.py -l mediumMaze -z .5 -p SearchAgent -a fn=ucs`.
5. **Custom Layout Naming:**  
   Resolved to `layouts/24i3025Search.lay` to follow Section 4, Section 5, and student roll number conventions.
6. **CSV Schema for Uninformed Search:**  
   $g, h, f$ columns are maintained across all algorithms; for DFS/BFS, $h=0$ and $f=g$ to preserve uniform CSV schemas.
7. **Team Size vs. Submission Filename:**  
   Both group members (`24i-3025` and `24i-3135`) are documented in the submission documentation, while the layout file is prefixed with `24i3025Search.lay`.
8. **Protected Inline Comments:**  
   All 7 `# DO NOT CHANGE` lines and protected classes (`SearchAgent`, `PositionSearchProblem`, `FoodSearchProblem`) in `searchAgents.py` are strictly preserved.

---

## 🚀 Quick Start & Environment Setup

Verify Python 3 (Python 3.7+ recommended) is installed:
```bash
python --version
# or
python3 --version
```

Navigate to the project directory and test running the base game:
```bash
cd search/search
python pacman.py
```

---

## 🧪 Search Tasks & Execution Commands

### Task 1: Depth-First Search (DFS)
```bash
python pacman.py -l tinyMaze -p SearchAgent -a fn=dfs
python pacman.py -l mediumMaze -p SearchAgent -a fn=dfs
python pacman.py -l bigMaze -z .5 -p SearchAgent -a fn=dfs
python autograder.py -q q1
```

### Task 2: Breadth-First Search (BFS)
```bash
python pacman.py -l mediumMaze -p SearchAgent -a fn=bfs
python pacman.py -l bigMaze -z .5 -p SearchAgent -a fn=bfs
python autograder.py -q q2
```

### Task 3: Uniform-Cost Search (UCS)
```bash
python pacman.py -l mediumMaze -p SearchAgent -a fn=ucs
python pacman.py -l mediumMaze -z .5 -p SearchAgent -a fn=ucs
python pacman.py -l mediumMaze -p StayEastSearchAgent
python autograder.py -q q3
```

### Task 4: Greedy Best-First Search (GBFS)
```bash
python pacman.py -l bigMaze -z .5 -p SearchAgent -a fn=gbfs,heuristic=manhattanHeuristic
python pacman.py -l bigMaze -z .5 -p SearchAgent -a fn=gbfs,heuristic=euclideanHeuristic
```

### Task 5: A* Search
```bash
python pacman.py -l bigMaze -z .5 -p SearchAgent -a fn=astar,heuristic=nullHeuristic
python pacman.py -l bigMaze -z .5 -p SearchAgent -a fn=astar,heuristic=manhattanHeuristic
python autograder.py -q q4
```

### Task 6: Multi-Goal Search (Corners Problem)
```bash
python pacman.py -l tinyCorners -p SearchAgent -a fn=bfs,prob=CornersProblem
python pacman.py -l mediumCorners -p AStarCornersAgent -z .5
python autograder.py -q q5
python autograder.py -q q6
```

### Task 7: Eating All Food Dots & Nearest Food Search
```bash
python pacman.py -l trickySearch -p AStarFoodSearchAgent
python pacman.py -l bigSearch -p ClosestDotSearchAgent
python autograder.py -q q7
python autograder.py -q q8
```

### Section 4: Custom Maze Testing
```bash
python pacman.py -l 24i3025Search -p SearchAgent -a fn=dfs
python pacman.py -l 24i3025Search -p SearchAgent -a fn=bfs
python pacman.py -l 24i3025Search -p SearchAgent -a fn=ucs
python pacman.py -l 24i3025Search -p SearchAgent -a fn=gbfs,heuristic=manhattanHeuristic
python pacman.py -l 24i3025Search -p SearchAgent -a fn=astar,heuristic=manhattanHeuristic
```

### Complete Autograder Run
```bash
python autograder.py --no-graphics
```

---

## 📋 Ticket Backlog Index (`tickets.md`)

| Ticket ID | Title | Module | Autograder | Status |
|:---|:---|:---|:---|:---|
| **AI-00** | Environment & Workspace Setup | Core / Infra | — | Pending |
| **AI-01** | Task 1 — Depth-First Search | `search.py` | `q1` | Pending |
| **AI-02** | Task 2 — Breadth-First Search | `search.py` | `q2` | Pending |
| **AI-03** | Task 3 — Uniform-Cost Search | `search.py` | `q3` | Pending |
| **AI-04** | Task 4 — Greedy Best-First Search | `search.py` | Manual / Sanity | Pending |
| **AI-05** | Task 5 — A* Search | `search.py` | `q4` | Pending |
| **AI-06** | Task 6a — Corners Problem State Space | `searchAgents.py` | `q5` | Pending |
| **AI-07** | Task 6b — Corners Heuristic | `searchAgents.py` | `q6` | Pending |
| **AI-08** | Task 7a — Food Heuristic (MST / bottleneck) | `searchAgents.py` | `q7` | Pending |
| **AI-08b** | Task 7b — AnyFoodSearchProblem & ClosestDot | `searchAgents.py` | `q8` | Pending |
| **AI-09** | CSV Trace Logger (Section 3, cross-cutting) | `search.py` | Manual QA | Pending |
| **AI-10** | Custom Layout + 5-Algorithm Matrix | Layouts / Exp | Manual / Screenshots | Pending |
| **AI-11** | README.txt | Documentation | — | Pending |
| **AI-12** | report.pdf (6–10 pages) | Documentation | — | Pending |
| **AI-13** | Full Autograder Pass + Final Packaging | Packaging / QA | `q1`–`q8` | Pending |

---

## 🎯 Evaluation Rubric Summary (150 Marks Total)

- **Automated Test Cases Execution (20 Marks):** 100% pass across standard tests and search problems.
- **Live Demonstration / Viva Defense (20 Marks):** Live code walkthrough, answering line-by-line questions.
- **Search Implementations (50 Marks):** A* (10), UCS (10), DFS (10), BFS (10), GBFS (10).
- **Heuristic Design & Multi-Goal (20 Marks):** Admissibility/consistency proofs (10), Corners/Food state space (10).
- **Execution Logging & Custom Experiments (20 Marks):** Automated CSV logging in `evidence/` (10), custom `.lay` maze & tables (10).
- **Documentation & Code Quality (20 Marks):** Comprehensive report.pdf (10), clean Python code & formatting (10).

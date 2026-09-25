# Pacman Search Project — Ticket Backlog
Course: AI2002 – Assignment 01 (Search) · Deadline: 27 Sept 2026 · Total: 150 marks

Verified against the actual contents of `search.zip` (Berkeley Pacman search framework) and cross-checked
line-by-line against the PDF. Everything below is scoped to what's really in the code, not just the PDF text.

**Guidance this backlog follows (from TA thread with Jaweria):** "Ma'am said follow the PDF instructions and
write code where required only." → In practice this means: implement things exactly where the starter code has
a `"*** YOUR CODE HERE ***"` marker or an explicitly-editable file (`search.py`, `searchAgents.py`,
`layouts/[YourID]Search.lay`), never touch a file on the forbidden list, and where the PDF conflicts with the
actual code, prefer a solution that satisfies the PDF's *intent* without editing forbidden files — documented
per-ticket below.

**Suggested loop per ticket:** `/tdd` (write the failing test / run the relevant `autograder.py -q qN` first to
confirm it fails) → `/implement` → `/code-review` → fix → `/code-review` again → repeat until clean →
run the *given* autograder question + the PDF's manual `pacman.py` commands → only then mark the ticket Done.
Do this per ticket, not once at the end — GBFS and the CSV logger have no autograder safety net, so catching
mistakes early matters more there than anywhere else.

---

## 0. READ FIRST — Inconsistencies Found (PDF vs. actual starter code)

These are real discrepancies discovered by extracting `search.zip` and reading `search.py`, `searchAgents.py`,
`util.py`, `layouts/`, and the `test_cases/` CONFIGs — not guesses. Each ticket below links back to the
relevant numbered item here. If your TA/ma'am gives a different ruling before submission, only the
"Resolution used" lines need updating.

1. **Forbidden-file list vs. CSV logging requirement.**
   PDF Step 3 forbids editing `pacman.py`, `game.py`, `util.py`, `layout.py`, `graphicsDisplay.py`,
   `graphicsUtils.py`, `textDisplay.py`. Section 3 requires every algorithm run to write a CSV trace.
   **Resolution used:** the CSV logger is implemented entirely inside `search.py` (the one file that already
   owns every expansion loop), using Python's stdlib `csv` module. No forbidden file needs to change. If a
   ticket ever *seems* to need a forbidden file touched, stop and flag it — it means the approach is wrong, not
   that the rule is optional.

2. **Task 4 (GBFS) does not exist in the starter code and has no autograder question.**
   `search.py` ships stubs for `depthFirstSearch`, `breadthFirstSearch`, `uniformCostSearch`, `aStarSearch` only
   — there is no `greedyBestFirstSearch` function or `gbfs` abbreviation anywhere, and `test_cases/` only
   contains `q1`–`q8` (DFS, BFS, UCS, A*, Corners-state-space, Corners-heuristic, Food-heuristic, Closest-dot).
   `SearchAgent.__init__` resolves `fn=` dynamically via `getattr(search, fn)`, so adding
   `greedyBestFirstSearch` + `gbfs = greedyBestFirstSearch` to `search.py` is enough for the CLI command in the
   PDF to work — but **there is no official test case to grade correctness against.**
   **Resolution used:** Ticket AI-04 implements GBFS as a straightforward priority-queue-on-`h(n)` search
   (same shape as UCS but priority = heuristic only), and adds our own manual sanity checks (see AI-04) since
   the autograder can't verify it. Flag this explicitly to the TA before viva — don't assume silence means it's
   ungraded.

3. **Mandatory "North → East → South → West" expansion order conflicts with the untouchable successor
   function.**
   PDF Task 1 says successors must expand N→E→S→W. But `PositionSearchProblem.getSuccessors` in
   `searchAgents.py` — explicitly commented `"this search problem is fully specified; you should NOT change
   it"` — generates successors in **North, South, East, West** order, not N-E-S-W.
   **Resolution used:** do *not* edit `PositionSearchProblem`. Instead, inside `search.py`, re-order the
   successor list returned by `getSuccessors()` into N→E→S→W (a tiny `DIRECTION_PRIORITY` dict + `sorted(...)`
   or manual reorder) before pushing onto the fringe. This satisfies the literal PDF requirement while
   respecting the "don't touch this file" comment.
   **TA ruling received:** the teacher said to do exactly what the PDF specifies and not change any protected
   code. Therefore `fn=dfs` enforces N-E-S-W inside `search.py`. The supplied q1 path fixture expects the
   conflicting natural order; neither that fixture nor `PositionSearchProblem` is changed.

4. **Two of the three UCS example commands reference things that don't exist.**
   PDF Task 3 gives:
   `python pacman.py -l mediumDenselyMaze -p SearchAgent -a fn=ucs` → `mediumDenselyMaze.lay` is **not** in
   `layouts/` (confirmed by listing the folder — 34 `.lay` files, none named this).
   `python pacman.py -l stayEastSearch -p SearchAgent -a fn=ucs` → there is no `stayEastSearch.lay` either, and
   more importantly this is the wrong *kind* of flag: directional cost bias in this codebase is implemented as
   an **agent**, not a layout — `StayEastSearchAgent` (in `searchAgents.py`) hardcodes
   `costFn = lambda pos: .5 ** pos[0]` and `self.searchFunction = search.uniformCostSearch` itself.
   **Resolution used:** run the PDF's first UCS command as-is (`mediumMaze`, which exists), and substitute the
   other two with the working equivalents:
   `python pacman.py -l mediumMaze -p SearchAgent -a fn=ucs -z .5` (in place of mediumDenselyMaze — use an
   existing dense-ish maze, note the substitution) and
   `python pacman.py -l mediumMaze -p StayEastSearchAgent` (the real way to exercise directional cost UCS).
   Document both the literal PDF command (and that it errors: *"... is not a layout file"*) and the substitute
   in the report/README, so the TA sees you noticed the discrepancy rather than silently changing it.

5. **Custom layout filename is specified two different ways.**
   Step 2 says create a file "inside the `layouts/` folder named [`layouts/Search.lay`]" (literally
   `Search.lay`). Section 4 says name it `layouts/[YourID]Search.lay`, e.g. `21I1234Search.lay`.
   **Resolution used:** follow Section 4 — it's the more specific instruction with a worked example, and the
   ZIP structure diagram at the end of the PDF also shows `[YourID]Search.lay` under `layouts/`. Ticket AI-09
   uses the ID-prefixed name.

6. **CSV schema asks for `g, h, f` columns on every algorithm, including DFS/BFS which have no heuristic.**
   Section 3's "Mandatory CSV Columns" list is stated to apply to "every algorithm execution," but DFS/BFS are
   uninformed searches with no `h(n)`/`f(n)` concept.
   **Resolution used:** keep the CSV schema identical across all five algorithms as literally mandated. For
   DFS/BFS: `g` = path cost accumulated so far (still meaningful), `h` = `0`, `f` = `g` (since there's no
   heuristic to add). This keeps every log file schema-compatible for the report's comparison tables without
   inventing numbers that don't exist.

7. **Team size vs. submission identity.** PDF says work in groups of 2–3, but the rubric page has a single
   "Student Name / Roll number" line and the custom layout is named after one ID. Not a code issue — just list
   every group member's name and roll number in `README.txt` (see AI-11) so nobody's left off.
   **This group:** 24i-3025 and 24i-3135 — both go in README (AI-11); the custom layout filename (AI-10) uses
   `24i3025Search.lay`, since the PDF's own example (`21I1234Search.lay`) is a single ID with no group
   convention — flag to the TA that it's ambiguous for a 2-person team and this is the assumption made.

8. **Inline `# DO NOT CHANGE` markers *inside* the files you're allowed to edit.** This is different from
   Inconsistency #1 (whole forbidden files) — `search.py` and `searchAgents.py` are editable, but several
   specific lines *inside* them are individually marked off-limits, because the autograder and the on-screen
   node-expansion counter depend on them. Confirmed by grep, exact locations:
   | File | Line (as shipped) | What it does |
   |---|---|---|
   | `searchAgents.py` | `SearchAgent` class, whole class (~L51–129) | "You should NOT change any code in SearchAgent" — resolves `fn=`/`heuristic=` strings via `getattr`; this is *why* AI-04's new `gbfs` function needs zero changes here. |
   | `searchAgents.py` | `PositionSearchProblem` class, whole class (~L130–216) | "fully specified; you should NOT change it" — see Inconsistency #3. |
   | `searchAgents.py` | `self._visited, self._visitedlist, self._expanded = {}, [], 0 # DO NOT CHANGE` (inside `PositionSearchProblem.__init__`) | Display/autograder bookkeeping. |
   | `searchAgents.py` | `self._expanded += 1 # DO NOT CHANGE` (inside `PositionSearchProblem.getSuccessors`) | Node-expansion counter the autograder reads. |
   | `searchAgents.py` | `self._expanded = 0 # DO NOT CHANGE` (inside `CornersProblem.__init__`) | Same, for AI-06. |
   | `searchAgents.py` | `self._expanded += 1 # DO NOT CHANGE` (inside `CornersProblem.getSuccessors`) | Keep this line at the end of the loop you write for AI-06. |
   | `searchAgents.py` | `CornersProblem.getCostOfActions` — "This is implemented for you" | Don't touch, for AI-06/AI-07. |
   | `searchAgents.py` | `FoodSearchProblem` class, whole class (~L362–411), incl. two more `# DO NOT CHANGE` on `self._expanded` | Entirely given — for AI-08 you only ever write the standalone `foodHeuristic` function outside this class. Note it also hands you `self.heuristicInfo = {}` for memoization — use it if your MST/bottleneck heuristic needs to cache anything across calls, rather than adding new instance state to the class. |
   | `searchAgents.py` | `AnyFoodSearchProblem.__init__` — `self._visited, self._visitedlist, self._expanded = {}, [], 0 # DO NOT CHANGE` | Already given for AI-08b; you only fill in `isGoalState`. |
   | `search.py` | `SearchProblem` class, whole class (~L11–48) | "You do not need to change anything in this class, ever." — not touched by any ticket, listed for completeness. |

   **Why this matters for AI-13's final check:** the file-level `diff` in AI-13 only protects the *forbidden*
   files (`pacman.py`, `game.py`, etc.) — `search.py` and `searchAgents.py` are *supposed* to change, so a diff
   against the original there would show everything as different and tell you nothing. Instead, AI-13 now
   includes a **line-presence grep** to confirm these specific markers survived inside your edited files (see
   updated AI-13 below). Each ticket touching these classes now explicitly calls out its own "don't touch"
   lines too.

---

## Ticket Index

| ID | Title | Depends on | Autograder |
|----|-------|-----------|------------|
| AI-00 | Environment & workspace setup | — | — |
| AI-01 | Task 1 — Depth-First Search | AI-00 | `q1` |
| AI-02 | Task 2 — Breadth-First Search | AI-00 | `q2` |
| AI-03 | Task 3 — Uniform-Cost Search | AI-00 | `q3` |
| AI-04 | Task 4 — Greedy Best-First Search (no autograder — see Inconsistency #2) | AI-00 | none |
| AI-05 | Task 5 — A* Search | AI-03 | `q4` |
| AI-06 | Task 6 — Corners Problem (state space) | AI-05 | `q5` |
| AI-07 | Task 6 — Corners Heuristic | AI-06 | `q6` |
| AI-08 | Task 7 — Food Heuristic (MST/bottleneck) | AI-07 | `q7` |
| AI-08b | Task 7 — AnyFoodSearchProblem / ClosestDotSearchAgent | AI-02 | `q8` |
| AI-09 | CSV trace logger (cross-cutting, Section 3) | AI-01…AI-08b | none (manual QA) |
| AI-10 | Custom layout + 5-algorithm experiment matrix (Section 4) | AI-01…AI-08b, AI-09 | none |
| AI-11 | README.txt | all above | — |
| AI-12 | report.pdf (6–10 pages) | AI-10 | — |
| AI-13 | Full autograder pass + final packaging | all above | `q1`–`q8` |

---

## AI-00 · Environment & Workspace Setup
**Type:** chore · **Priority:** P0 · **Depends on:** —
**Files touched:** none (verification only)

### Context
Confirm the extracted `search.zip` matches what the PDF assumes before writing any code.

### Acceptance Criteria
- [x] `search.zip` extracted with folder structure intact (`layouts/`, `test_cases/`, all root `.py` files present).
- [x] `python3 --version` ≥ 3.7 confirmed and recorded (for README later: Python 3.14.7).
- [x] `python pacman.py` runs with no search logic and shows the game window / text display without crashing.
- [x] `python autograder.py -q q1` run once *before* any code is written, to confirm it currently fails
      (baseline — this is your `/tdd` red state for AI-01: 0/3).
- [x] Confirm which files are actually editable vs. forbidden by grepping for `"*** YOUR CODE HERE ***"` — only
      `search.py` and `searchAgents.py` should contain these markers. If any forbidden file also contains one,
      flag it immediately (verified: only search.py and searchAgents.py).
- [x] Create `evidence/` and `evidence/screenshots/` directories (required by Section 5's ZIP layout, not
      present in the starter).

### Notes
No `report.pdf`, `README.txt`, or `evidence/` folder ship in the zip — all three are deliverables you create
(tracked in AI-09, AI-11, AI-12).

---

## AI-01 · Task 1 — Depth-First Search
**Type:** feature · **Priority:** P0 · **Depends on:** AI-00
**Files touched:** `search.py` only (`depthFirstSearch`)

### Context
Implement `depthFirstSearch` in `search.py`. See **Inconsistency #3** — the mandated N→E→S→W order must be
enforced *inside* `search.py`, not by editing `searchAgents.py`.

### Acceptance Criteria
- [ ] Uses `util.Stack` as the fringe (LIFO) — no other data structure.
- [ ] Strict **graph search**: maintains an explicit explored/closed set; a state is never expanded twice, and
      states already in `explored` are not re-pushed.
- [ ] Successor order is forced to North → East → South → West via a small shared helper (e.g.
      `reorderSuccessors(successors)`), applied on top of whatever order `getSuccessors()` returns — do **not**
      modify `PositionSearchProblem`.
- [ ] Returns a list of action strings (e.g. `['North','East','South']`) that reaches the goal; returns `[]` if
      start is already the goal; returns `None`/empty when unsolvable rather than crashing.
- [ ] Handles `tinyMaze`, `mediumMaze`, `bigMaze` without recursion-limit errors (implement iteratively with the
      stack, not via Python recursion).
- [ ] **Do not touch** `PositionSearchProblem` in `searchAgents.py` at all (whole class marked "fully
      specified... should NOT change it," Inconsistency #8) — the N-E-S-W reorder happens purely on the list
      `search.py` receives back from `getSuccessors()`, never inside that method itself.

### Test Commands
```
python pacman.py -l tinyMaze -p SearchAgent -a fn=dfs
python pacman.py -l mediumMaze -p SearchAgent -a fn=dfs
python pacman.py -l bigMaze -z .5 -p SearchAgent -a fn=dfs
python autograder.py -q q1
```
### Definition of Done
`autograder.py -q q1` passes 100%, all three manual commands find a valid path, `/code-review` run at least
once with zero open comments.

---

## AI-02 · Task 2 — Breadth-First Search
**Type:** feature · **Priority:** P0 · **Depends on:** AI-00
**Files touched:** `search.py` only (`breadthFirstSearch`)

### Acceptance Criteria
- [ ] Uses `util.Queue` (FIFO) as the fringe.
- [ ] Graph search with explored set; a state already in the frontier **or** explored set is never re-enqueued
      (check membership before pushing, not just before popping — this is the classic BFS bug that breaks
      optimality).
- [ ] On unweighted mazes, returns a shortest path in step count — verify by comparing path length against
      `autograder.py`'s solution files (it checks this for you, but sanity-check manually on `mediumMaze` too).
- [ ] Does **not** apply the N-E-S-W reorder from AI-01 unless AI-01's open question (Inconsistency #3) gets
      resolved as "applies globally" — the PDF places the rule under DFS, so BFS remains unchanged.

### Test Commands
```
python pacman.py -l mediumMaze -p SearchAgent -a fn=bfs
python pacman.py -l bigMaze -z .5 -p SearchAgent -a fn=bfs
python autograder.py -q q2
```

---

## AI-03 · Task 3 — Uniform-Cost Search
**Type:** feature · **Priority:** P0 · **Depends on:** AI-00
**Files touched:** `search.py` only (`uniformCostSearch`)

### Context
See **Inconsistency #4** — two of the three PDF example commands reference a nonexistent layout / wrong flag
shape. Both the literal and the corrected commands must be run and documented.

### Acceptance Criteria
- [ ] Uses `util.PriorityQueue` ordered by accumulated cost `g(n)`.
- [ ] When a cheaper path to a state already on the fringe is found, calls `PriorityQueue.update(item,
      newPriority)` (already provided in `util.py` — do not reimplement decrease-key by hand) instead of
      pushing a duplicate.
- [ ] Explored set prevents re-expansion of finalized (popped) states.
- [ ] Confirmed to find the true minimum-cost path on a weighted-cost problem (`StayEastSearchAgent`), not just
      the fewest steps.

### Test Commands
```
python pacman.py -l mediumMaze -p SearchAgent -a fn=ucs
python autograder.py -q q3

# PDF's literal commands (expected to fail — documents Inconsistency #4):
python pacman.py -l mediumDenselyMaze -p SearchAgent -a fn=ucs   # errors: no such layout
python pacman.py -l stayEastSearch -p SearchAgent -a fn=ucs      # errors: no such layout

# Working substitutes (use these for the actual experiment + screenshots):
python pacman.py -l mediumMaze -z .5 -p SearchAgent -a fn=ucs
python pacman.py -l mediumMaze -p StayEastSearchAgent
```
### Notes
Screenshot both the PDF's literal command failing and the substitute succeeding — this is exactly the kind of
evidence a "live viva" question could probe, per the rubric's "answering line-by-line questions" criterion.

---

## AI-04 · Task 4 — Greedy Best-First Search
**Type:** feature · **Priority:** P1 · **Depends on:** AI-00

**⚠️ No autograder coverage — see Inconsistency #2. Treat this ticket's own manual checks as the test suite.**

**Files touched:** `search.py` (new function `greedyBestFirstSearch` + `gbfs` abbreviation)

### Acceptance Criteria
- [ ] New function `greedyBestFirstSearch(problem, heuristic=nullHeuristic)` added to `search.py`, matching the
      signature shape of `aStarSearch` (so `SearchAgent`'s `'heuristic' in func.__code__.co_varnames` check
      picks it up automatically — no `searchAgents.py` changes needed).
- [ ] Priority queue ordered **strictly by `h(n)`** (not `g(n)+h(n)` — that's A*, don't accidentally paste the
      A* body and forget to drop `g`).
- [ ] Add `gbfs = greedyBestFirstSearch` to the abbreviations block at the bottom of `search.py`, next to
      `bfs`/`dfs`/`astar`/`ucs`.
- [ ] Works with both `manhattanHeuristic` and `euclideanHeuristic` from `searchAgents.py` passed via
      `heuristic=`.
- [ ] **Manual correctness check (since no autograder exists):** on `bigMaze`, compare GBFS's path length and
      nodes-expanded against A*'s (AI-05) on the same maze/heuristic — GBFS should expand fewer or comparable
      nodes but *may* return a longer path (that's the expected, correct behavior — GBFS is not optimal). If
      GBFS returns a *shorter* path than A* with an admissible heuristic on the same maze, that's a red flag —
      re-check the implementation.

### Test Commands
```
python pacman.py -l bigMaze -z .5 -p SearchAgent -a fn=gbfs,heuristic=manhattanHeuristic
```
### Notes
Flag to the TA before viva that this task has no official test case bundled with the project — be ready to
explain and defend correctness live, per the rubric's "Live Demonstration / Viva Defense" line (20 marks).

---

## AI-05 · Task 5 — A* Search
**Type:** feature · **Priority:** P0 · **Depends on:** AI-03 (reuses the same priority-queue-with-update pattern)
**Files touched:** `search.py` only (`aStarSearch`)

### Acceptance Criteria
- [ ] Priority queue ordered by `f(n) = g(n) + h(n)`.
- [ ] `g(n)` = accumulated path cost from start; `h(n)` = `heuristic(state, problem)` — don't drop the `problem`
      argument, some heuristics need it (e.g. `cornersHeuristic`, `foodHeuristic`).
- [ ] Frontier updates use `PriorityQueue.update` on cheaper `f(n)` discoveries, same as UCS.
- [ ] Verified optimal: with `nullHeuristic` (h=0, degenerates to UCS) and `manhattanHeuristic` (admissible +
      consistent on grid mazes with unit costs), both return the same optimal path cost on `bigMaze`.

### Test Commands
```
python pacman.py -l bigMaze -z .5 -p SearchAgent -a fn=astar,heuristic=nullHeuristic
python pacman.py -l bigMaze -z .5 -p SearchAgent -a fn=astar,heuristic=manhattanHeuristic
python autograder.py -q q4
```

---

## AI-06 · Task 6a — Corners Problem State Space
**Type:** feature · **Priority:** P0 · **Depends on:** AI-05 (q5 config depends on q4 in the CONFIG files)
**Files touched:** `searchAgents.py` only (`CornersProblem` class: `getStartState`, `isGoalState`,
`getSuccessors`)

### Acceptance Criteria
- [ ] State representation is `(pacman_position, tuple_of_visited_corners)` exactly as the PDF specifies —
      `tuple_of_visited_corners` must be a `tuple` (hashable, usable in the DFS/BFS explored set), not a list.
- [ ] `getStartState()` returns `(self.startingPosition, ())` (no corners visited yet).
- [ ] `isGoalState(state)` returns `True` iff all 4 corners are in the visited tuple.
- [ ] `getSuccessors(state)` follows the same `[NORTH, SOUTH, EAST, WEST]` loop shape already sketched in the
      comment, checks walls the same way `PositionSearchProblem` does, and — when a successor position matches
      an unvisited corner — adds it to the new state's visited tuple.
- [ ] Increments `self._expanded` exactly once per call (marked `DO NOT CHANGE` — keep that line as-is).
- [ ] **Do not touch:** `self._expanded = 0 # DO NOT CHANGE` in `__init__`, the `self._expanded += 1 # DO NOT
      CHANGE` line already sitting at the end of `getSuccessors` (write your loop above it, don't move or
      delete it), or `getCostOfActions` ("This is implemented for you" — leave as shipped). See Inconsistency
      #8 for the full line-by-line list.

### Test Commands
```
python pacman.py -l tinyCorners -p SearchAgent -a fn=bfs,prob=CornersProblem
python pacman.py -l mediumCorners -p SearchAgent -a fn=bfs,prob=CornersProblem
python autograder.py -q q5
```

---

## AI-07 · Task 6b — Corners Heuristic
**Type:** feature · **Priority:** P0 · **Depends on:** AI-06
**Files touched:** `searchAgents.py` only (`cornersHeuristic`)

### Acceptance Criteria
- [ ] Heuristic is a function of `(remaining unvisited corners, current position)` only — never inspects the
      actual maze walls beyond what's passed in `problem.walls`, and never calls the real search algorithms
      recursively (that would defeat the point and blow up runtime).
- [ ] Mathematically admissible: never overestimates true remaining cost. Simplest defensible choice: sum of
      Manhattan distances along a greedy nearest-unvisited-corner tour, or max-of-Manhattan-to-farthest-corner
      — document which one is used and include the admissibility argument in the report (AI-12).
- [ ] Consistent: `h(n) <= cost(n, n') + h(n')` for every successor `n'` — spot-check this on a few transitions
      manually or via a quick script, since `autograder.py -q q6` (Q6PartialCreditQuestion) grades both
      correctness *and* node-expansion efficiency, not just admissibility.
- [ ] `AStarCornersAgent` (already wired to `cornersHeuristic` — don't touch that class) finds the optimal tour
      on `mediumCorners`.
- [ ] **Do not touch** `CornersProblem.getCostOfActions` (already implemented) or either `# DO NOT CHANGE`
      `self._expanded` line from AI-06 while iterating on the heuristic.

### Test Commands
```
python pacman.py -l mediumCorners -p AStarCornersAgent -z .5
python autograder.py -q q6
```

---

## AI-08 · Task 7a — Food Heuristic (MST / bottleneck)
**Type:** feature · **Priority:** P1 · **Depends on:** AI-07
**Files touched:** `searchAgents.py` only (`foodHeuristic`)

### Acceptance Criteria
- [ ] Admissible and (ideally) consistent heuristic for `FoodSearchProblem`, using either a minimum spanning
      tree over remaining food + current position, or max-Manhattan/maze-distance to the farthest remaining
      dot (bottleneck) — pick one, document the choice and complexity in the report.
- [ ] If using true maze distance rather than Manhattan distance, reuse `mazeDistance()` (already implemented
      at the bottom of `searchAgents.py`, built on `search.bfs`) rather than writing a new BFS — this is
      exactly what it's there for.
- [ ] Node-expansion count on `trickySearch` is checked against the autograder's efficiency thresholds
      (`PartialCreditQuestion` — this one grades on a curve, not pass/fail).
- [ ] No `util.raiseNotDefined()` left in the function.
- [ ] **Do not touch `FoodSearchProblem` at all** — the whole class (`__init__`, `getStartState`,
      `isGoalState`, `getSuccessors` incl. its two `# DO NOT CHANGE` `self._expanded` lines, and
      `getCostOfActions`) ships fully implemented; `foodHeuristic` is the only thing you write, as a standalone
      function outside the class. If a caching need comes up, use the `self.heuristicInfo = {}` dict the class
      already provides instead of adding new state to `FoodSearchProblem`.

### Test Commands
```
python pacman.py -l trickySearch -p AStarFoodSearchAgent
python autograder.py -q q7
```
### Notes
This is the highest-risk ticket for silent performance failure — it can return a technically-admissible but
weak heuristic that passes correctness but scores poorly on the partial-credit node-expansion curve. Budget
extra `/code-review` passes here specifically checking Big-O of the heuristic itself (an O(n²) MST computed on
every single node expansion will make `trickySearch` painfully slow).

---

## AI-08b · Task 7b — AnyFoodSearchProblem & ClosestDotSearchAgent
**Type:** feature · **Priority:** P0 · **Depends on:** AI-02 (reuses BFS)
**Files touched:** `searchAgents.py` only (`AnyFoodSearchProblem.isGoalState`,
`ClosestDotSearchAgent.findPathToClosestDot`)

### Acceptance Criteria
- [ ] `AnyFoodSearchProblem.isGoalState(state)` returns `True` iff `self.food[x][y]` is `True` — i.e. any food
      dot, not a fixed single goal like `PositionSearchProblem`.
- [ ] `findPathToClosestDot` builds an `AnyFoodSearchProblem(gameState)` and solves it with **BFS specifically**
      (`search.breadthFirstSearch`), as the PDF requires — not UCS/A*, since all step costs are 1 here anyway
      and BFS is what the PDF names.
- [ ] `ClosestDotSearchAgent.registerInitialState` (already implemented, don't touch) repeatedly calls this
      until all food is gone — verify the returned path never contains an illegal move (it already asserts
      this and will raise an exception if your goal test is wrong).
- [ ] **Do not touch** `AnyFoodSearchProblem.__init__` (its `# DO NOT CHANGE` line covers
      `self._visited, self._visitedlist, self._expanded`) — `isGoalState` is the only method you write.

### Test Commands
```
python pacman.py -l bigSearch -p ClosestDotSearchAgent
python autograder.py -q q8
```

---

## AI-09 · CSV Trace Logger (Section 3, cross-cutting)
**Type:** feature · **Priority:** P0 · **Depends on:** AI-01, AI-02, AI-03, AI-04, AI-05 (needs all five
algorithms implemented to log against)
**Files touched:** `search.py` only

### Context
See **Inconsistencies #1 and #6**. This is deliberately its own ticket rather than folded into AI-01…AI-05,
because it's cross-cutting logging infrastructure, not part of any single algorithm's correctness — but every
correctness ticket above must still pass its autograder question *unmodified in behavior* once logging is
added. Logging must be a side effect, never change what gets returned.

### Acceptance Criteria
- [ ] A single shared logging helper in `search.py` (e.g. `_logExpansion(...)` / a small `SearchLogger` class)
      used by all five search functions, writing to `evidence/<algorithm>_<layout>_<timestamp>.csv` — don't
      duplicate CSV-writing code five times.
- [ ] Exact mandatory columns, in order:
      `iteration, expanded_state, parent, action, generated_successors, frontier_before, frontier_after, explored, g, h, f`
- [ ] One row per **expanded** state (not per push), `iteration` is a monotonically increasing counter starting
      at 0 or 1 (pick one, be consistent).
- [ ] `frontier_before`/`frontier_after` are serialized snapshots of the fringe's contents at that iteration
      (e.g. `str(list(...))`) — acceptable to stringify, doesn't need to be machine-parseable beyond CSV cells.
- [ ] For DFS/BFS: `h` = `0`, `f` = `g` (per Inconsistency #6) — don't leave these blank/`None`, which would
      break any pandas/Excel analysis in the report.
- [ ] Adding the logger does **not** change `autograder.py -q q1`–`q4` pass/fail results — re-run all four after
      wiring in logging to confirm no regression (this is exactly the kind of thing `/code-review` should catch
      before you move on).
- [ ] Confirms zero changes to any file on the forbidden list (Inconsistency #1) — logger lives entirely in
      `search.py`.

### Test Commands
```
# Re-run every autograder question after adding logging — must still be 100%:
python autograder.py -q q1
python autograder.py -q q2
python autograder.py -q q3
python autograder.py -q q4

# Then generate the actual evidence CSVs for the report, one per task's example commands from AI-01..AI-05.
```

---

## AI-10 · Custom Layout + 5-Algorithm Experiment Matrix (Section 4)
**Type:** feature/experiment · **Priority:** P1 · **Depends on:** AI-01…AI-08b, AI-09
**Files touched:** `layouts/24i3025Search.lay` (new file — see Inconsistencies #5 and #7 for naming)

### Acceptance Criteria
- [ ] New `.lay` file at `layouts/24i3025Search.lay`, following the character
      conventions of existing files in `layouts/` (`%` = wall, `.` = food, `P` = Pacman start — check an
      existing small layout like `smallSearch.lay` for the exact grammar `layout.py` expects, since `layout.py`
      itself is forbidden to edit and therefore authoritative on the format).
- [ ] Contains multiple decision branches, at least one dead end, and at least one "deceptive trap" — a
      short-looking corridor that's actually a local-heuristic trap — specifically designed so GBFS
      (heuristic-only) takes a visibly worse/longer path than A* on the same maze.
- [ ] All 5 algorithms (DFS, BFS, UCS, GBFS, A*) run successfully on the new layout with no crashes.
- [ ] Screenshot captured for each of the 5 runs, saved under `evidence/screenshots/`.
- [ ] CSV log generated for each of the 5 runs via AI-09's logger, saved under `evidence/`.

### Test Commands
```
python pacman.py -l 24i3025Search -p SearchAgent -a fn=dfs
python pacman.py -l 24i3025Search -p SearchAgent -a fn=bfs
python pacman.py -l 24i3025Search -p SearchAgent -a fn=ucs
python pacman.py -l 24i3025Search -p SearchAgent -a fn=gbfs,heuristic=manhattanHeuristic
python pacman.py -l 24i3025Search -p SearchAgent -a fn=astar,heuristic=manhattanHeuristic
```

---

## AI-11 · README.txt
**Type:** docs · **Priority:** P2 · **Depends on:** all implementation tickets substantially complete
**Files touched:** `README.txt` (new)

### Acceptance Criteria
- [ ] Python version used (from AI-00) and OS/system specs.
- [ ] Exact run commands for every task (copy from each ticket's Test Commands section).
- [ ] Both group members listed explicitly (per Inconsistency #7 — rubric page only has room for one line, list
      both anyway): **24i-3025** and **24i-3135** (add full names).
- [ ] Short note listing the deliberate PDF/code discrepancies (Section 0 above, condensed to a few lines) so
      the TA sees they were noticed and handled, not missed.

---

## AI-12 · report.pdf (6–10 pages)
**Type:** docs · **Priority:** P1 · **Depends on:** AI-10
**Files touched:** `report.pdf` (new)

### Acceptance Criteria
- [ ] Space/time complexity analysis for each of the 5 algorithms.
- [ ] State space description for `CornersProblem` and `FoodSearchProblem`.
- [ ] Admissibility/consistency proof (or argument) for `cornersHeuristic` and `foodHeuristic`.
- [ ] Empirical performance table (nodes expanded, path cost, time) across standard mazes **and** the custom
      layout — pull numbers straight from the AI-09 CSV logs rather than re-timing by hand.
- [ ] Screenshot comparison of GBFS vs. A* on the custom layout, explicitly calling out the "deceptive trap"
      from AI-10 and why GBFS falls for it while A* doesn't.
- [ ] A short appendix documenting Inconsistencies #3 and #4 (the ordering ambiguity and the broken UCS
      example commands) with before/after screenshots — this directly serves the rubric's "Report & Complexity
      Analysis" (10 marks) and doubles as viva prep.

---

## AI-13 · Full Autograder Pass + Final Packaging
**Type:** chore/release · **Priority:** P0 · **Depends on:** everything above
**Files touched:** none (verification + zip)

### Acceptance Criteria
- [ ] `python autograder.py` (no `-q`, runs everything) passes **100%** across `q1`–`q8` with no manual
      intervention, on a clean re-extraction of the final submission (not just your working directory — this
      catches "works on my machine" path issues).
- [ ] `evidence/` contains CSV logs for every command listed across AI-01–AI-10, plus `evidence/screenshots/`.
- [ ] Final ZIP matches the exact structure from PDF Section 5: unmodified `pacman.py`, `game.py`, `util.py`,
      `layout.py`; edited `search.py` and `searchAgents.py`; `README.txt`; `report.pdf`; `layouts/` with the
      custom file added; `evidence/` with CSVs and screenshots.
- [ ] Print the rubric table (from the PDF's last page) for the viva, per Step "Bring its print during viva."
- [ ] Diff the submission's `pacman.py`, `game.py`, `util.py`, `layout.py`, `graphicsDisplay.py`,
      `graphicsUtils.py`, `textDisplay.py` against the original `search.zip` versions — must be byte-identical.
      This is the single check that most directly protects the "100% passing rate on standard tests" (20 marks)
      and "strict adherence to provided interface rules" (part of the 10-mark code quality line) rubric items.
- [ ] **Separately**, since `search.py`/`searchAgents.py` *are* supposed to differ from the original (a whole-
      file diff tells you nothing useful there), grep them for every Inconsistency #8 marker and confirm each
      one is still present, unmodified, inside its original method:
      `SearchAgent` class untouched, `PositionSearchProblem` class untouched, `FoodSearchProblem` class
      untouched, and all seven `# DO NOT CHANGE` comment lines still present verbatim.

### Test Commands
```
diff -q pacman.py <original_search.zip>/pacman.py
diff -q game.py <original_search.zip>/game.py
diff -q util.py <original_search.zip>/util.py
diff -q layout.py <original_search.zip>/layout.py
diff -q graphicsDisplay.py <original_search.zip>/graphicsDisplay.py
diff -q graphicsUtils.py <original_search.zip>/graphicsUtils.py
diff -q textDisplay.py <original_search.zip>/textDisplay.py

# Inline-marker survival check (searchAgents.py IS allowed to change elsewhere — this only
# confirms the protected lines specifically weren't touched or deleted):
grep -c "# DO NOT CHANGE" searchAgents.py        # expect 7
grep -q "class SearchAgent" searchAgents.py && diff <(sed -n '/^class SearchAgent/,/^class PositionSearchProblem/p' searchAgents.py) <(sed -n '/^class SearchAgent/,/^class PositionSearchProblem/p' <original_search.zip>/searchAgents.py)
diff <(sed -n '/^class PositionSearchProblem/,/^class StayEastSearchAgent/p' searchAgents.py) <(sed -n '/^class PositionSearchProblem/,/^class StayEastSearchAgent/p' <original_search.zip>/searchAgents.py)
diff <(sed -n '/^class FoodSearchProblem/,/^class AStarFoodSearchAgent/p' searchAgents.py) <(sed -n '/^class FoodSearchProblem/,/^class AStarFoodSearchAgent/p' <original_search.zip>/searchAgents.py)

python autograder.py --no-graphics
```

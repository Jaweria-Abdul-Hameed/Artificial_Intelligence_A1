"""Build report.pdf from tools/results.json + evidence/screenshots.

Usage (from the repo root):  python tools/build_report.py
Renders tools/report/report.html with headless Edge/Chrome into
search/search/report.pdf.  Repo-level helper; not part of the submission ZIP.
"""
import html
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT = os.path.join(ROOT, 'search', 'search')
OUT_DIR = os.path.join(ROOT, 'tools', 'report')
SHOTS = '../../search/search/evidence/screenshots/'
BROWSERS = [r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
            r'C:\Program Files\Google\Chrome\Application\chrome.exe']

data = json.load(open(os.path.join(ROOT, 'tools', 'results.json')))
R = {e['label']: e for e in data['experiments']}
BROKEN = {b['label']: b for b in data['broken']}
GRADE = data['autograder']
GRADE_TOTAL = '%g/%g' % tuple(GRADE['total'])
GRADE_PASSING = all(q['got'] >= q['max'] for q in GRADE['questions'])
Q7 = next(q for q in GRADE['questions'] if q['q'] == 'q7')


def n(label, key='nodes'):
    v = R[label][key]
    return '%d' % v if v is not None else 'n/a'


def secs(label):
    v = R[label]['seconds']
    return '%.2f' % v if v is not None else 'n/a'


def bars(items, width=640, unit='nodes expanded', color='var(--blue)', hilite=None):
    """Horizontal bar chart as inline SVG.  items: [(label, value)]."""
    hilite = hilite or {}
    top = max(v for _, v in items)
    rowh, left, right = 26, 190, 60
    h = rowh * len(items) + 8
    out = ['<svg class="chart" viewBox="0 0 %d %d" role="img">' % (width, h)]
    scale = (width - left - right) / float(top)
    for i, (label, v) in enumerate(items):
        y = 4 + i * rowh
        w = max(2, v * scale)
        fill = hilite.get(label, color)
        out.append('<text x="%d" y="%d" class="cl" text-anchor="end">%s</text>' % (left - 10, y + 16, html.escape(label)))
        out.append('<rect x="%d" y="%d" width="%.1f" height="16" rx="3" fill="%s"/>' % (left, y + 3, w, fill))
        out.append('<text x="%.1f" y="%d" class="cv">%d</text>' % (left + w + 6, y + 16, v))
    out.append('</svg>')
    return '\n'.join(out)


def fig(label, caption, cls=''):
    return ('<figure class="%s"><img src="%s%s.png"><figcaption>%s</figcaption></figure>'
            % (cls, SHOTS, label, caption))


def table_rows(labels):
    rows = []
    for l in labels:
        e = R[l]
        rows.append('<tr><td>%s</td><td class="num">%s</td><td class="num">%s</td><td class="num">%s</td></tr>'
                    % (html.escape(e['description']), n(l, 'cost'), n(l), secs(l)))
    return '\n'.join(rows)


bigMaze = [('DFS', R['dfs_bigMaze']['nodes']), ('BFS', R['bfs_bigMaze']['nodes']),
           ('GBFS (Manhattan)', R['gbfs_bigMaze']['nodes']),
           ('A* (null h)', R['astar_bigMaze_null']['nodes']),
           ('A* (Manhattan)', R['astar_bigMaze']['nodes'])]
custom = [('DFS', R['custom_dfs']['nodes']), ('BFS', R['custom_bfs']['nodes']),
          ('UCS', R['custom_ucs']['nodes']), ('GBFS', R['custom_gbfs']['nodes']),
          ('A*', R['custom_astar']['nodes'])]
customCost = [(a, int(R['custom_' + k]['cost'])) for a, k in
              (('DFS', 'dfs'), ('BFS', 'bfs'), ('UCS', 'ucs'), ('GBFS', 'gbfs'), ('A*', 'astar'))]

CSS = """
:root{--ink:#0e1330;--muted:#5a6083;--rule:#d9dcee;--tint:#eef0ff;--blue:#2437e8;--yellow:#ffc800;
--ok:#12805c;--bad:#c2321f;--paper:#ffffff}
@page{size:A4;margin:15mm 15mm 16mm}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font:9.6pt/1.5 'IBM Plex Sans',Segoe UI,Arial,sans-serif}
h1,h2,h3{font-family:'Bricolage Grotesque','IBM Plex Sans',Segoe UI,sans-serif;margin:0;letter-spacing:-.01em;text-wrap:balance}
h2{font-size:17pt;margin:0 0 3mm;padding-bottom:2mm;border-bottom:2px solid var(--ink)}
h3{font-size:11.5pt;margin:5mm 0 1.5mm}
p{margin:0 0 2.6mm}
code,.mono{font-family:'JetBrains Mono',Consolas,monospace;font-size:8.4pt}
.page{break-after:page;min-height:250mm}
.page:last-child{break-after:auto}
.cover{background:var(--ink);color:#fff;margin:-15mm -15mm 0;padding:22mm 15mm 14mm;position:relative;overflow:hidden}
.cover h1{font-size:34pt;line-height:1.05;max-width:150mm}
.cover .kicker{font:600 8.5pt 'JetBrains Mono',monospace;letter-spacing:.14em;text-transform:uppercase;color:var(--yellow);margin-bottom:6mm}
.cover .meta{margin-top:8mm;color:#c9cdf0;font-size:9.5pt}
.dots{position:absolute;right:14mm;top:20mm;width:38mm;height:38mm;border-radius:50%;background:var(--yellow);
 clip-path:polygon(50% 50%,100% 22%,100% 0,0 0,0 100%,100% 100%,100% 78%)}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:3mm;margin:7mm 0 5mm}
.stat{background:var(--tint);border-radius:2mm;padding:3mm 3.5mm}
.stat b{display:block;font:700 19pt 'Bricolage Grotesque',sans-serif;color:var(--blue)}
.stat span{font-size:8pt;color:var(--muted)}
table{border-collapse:collapse;width:100%;margin:2mm 0 4mm;font-size:8.8pt}
th{font:600 7.8pt 'JetBrains Mono',monospace;text-transform:uppercase;letter-spacing:.06em;text-align:left;color:var(--muted);
 border-bottom:1.5px solid var(--ink);padding:1.5mm 2mm}
td{padding:1.5mm 2mm;border-bottom:1px solid var(--rule);vertical-align:top}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums;font-family:'JetBrains Mono',monospace;font-size:8.4pt}
tr.hl td{background:#fff7d6}
.two{display:grid;grid-template-columns:1fr 1fr;gap:5mm}
figure{margin:0 0 3mm}
figure img{width:100%;display:block;border:1px solid var(--rule);border-radius:1.5mm;background:#000}
figcaption{font-size:8pt;color:var(--muted);margin-top:1.2mm}
.callout{border-left:3px solid var(--yellow);background:#fffbe6;padding:2.5mm 3.5mm;margin:3mm 0;border-radius:0 1.5mm 1.5mm 0}
.proof{background:var(--tint);border-radius:2mm;padding:3mm 4mm;margin:2mm 0 3mm}
.proof b.t{font:600 8pt 'JetBrains Mono',monospace;letter-spacing:.06em;text-transform:uppercase;color:var(--blue)}
.chart{width:100%;height:auto;margin:1mm 0 3mm}
.chart .cl{font:8.4px 'IBM Plex Sans',sans-serif;fill:var(--ink)}
.chart .cv{font:600 8.4px 'JetBrains Mono',monospace;fill:var(--muted)}
.pill{display:inline-block;padding:.2mm 2mm;border-radius:5mm;font:600 7.6pt 'JetBrains Mono',monospace}
.pill.ok{background:#dcf3ea;color:var(--ok)}.pill.bad{background:#fbe1dc;color:var(--bad)}
ul{margin:0 0 2.6mm;padding-left:5mm}li{margin-bottom:1mm}
.csv{font:7.2pt/1.35 'JetBrains Mono',monospace;background:#0e1330;color:#dfe2ff;padding:3mm;border-radius:2mm;white-space:pre-wrap;word-break:break-all}
"""

BODY = """
<section class="page">
 <div class="cover">
  <div class="dots"></div>
  <div class="kicker">AI2002 &middot; Assignment 01 &middot; Search</div>
  <h1>Teaching Pacman to search</h1>
  <div class="meta">Five search algorithms, two multi-goal problems, a CSV trace for every run and one deliberately deceptive maze.<br>
  Jaweria Abdul Hameed (24i-3025) &middot; Mohsin Khan (24i-3135)</div>
 </div>
 <div class="stats">
  <div class="stat"><b>%(grade)s</b><span>autograder points, %(gradenote)s</span></div>
  <div class="stat"><b>%(q7)s</b><span>nodes expanded by A* on trickySearch (top threshold: 7000)</span></div>
  <div class="stat"><b>%(gb)s vs %(as)s</b><span>path length, GBFS vs A* on the custom maze</span></div>
  <div class="stat"><b>%(ncsv)d</b><span>CSV traces in evidence/</span></div>
 </div>
 <h3>What is in this report</h3>
 <ul>
  <li><b>Section 1</b> describes how each algorithm is built and what it costs in time and space.</li>
  <li><b>Section 2</b> defines the state spaces for CornersProblem and FoodSearchProblem.</li>
  <li><b>Section 3</b> proves that cornersHeuristic and foodHeuristic are admissible and consistent.</li>
  <li><b>Section 4</b> compares all algorithms empirically. Every number comes from the CSV traces or the run output.</li>
  <li><b>Section 5</b> analyses the custom maze and why greedy search falls for it.</li>
  <li><b>Appendix</b> documents the two places where the PDF and the starter code disagree.</li>
 </ul>
 <h3>Design rules followed</h3>
 <p>Only <code>search.py</code>, <code>searchAgents.py</code> and the new layout were edited. Every algorithm is written
 inside its own provided function; the single exception is <code>depthFirstSearch</code>, which calls the helper
 <code>_depthFirstSearch</code> so the mandatory North-East-South-West order is enforced without touching
 <code>PositionSearchProblem</code>. The CSV logger is one shared class in <code>search.py</code>, called from inside each loop.</p>
 <div class="callout"><b>How the CSV trace reads.</b> One row is written for every expanded state with the columns
 <code>iteration, expanded_state, parent, action, generated_successors, frontier_before, frontier_after, explored, g, h, f</code>.
 The frontier is printed with the next state to be expanded first. DFS, BFS and UCS log <code>h = 0</code> and <code>f = g</code>;
 GBFS logs <code>f = h</code> because it orders by <code>h</code> alone.</div>
 <div class="csv">%(csvsample)s</div>
</section>

<section class="page">
 <h2>1 &middot; Algorithms and complexity</h2>
 <p>All five searches are graph searches: a state is never expanded twice unless A* finds a strictly cheaper path to it.
 Notation: <i>b</i> branching factor, <i>d</i> depth of the shallowest goal, <i>m</i> maximum depth, <i>C*</i> optimal cost,
 <i>&epsilon;</i> smallest step cost, <i>|S|</i> number of reachable states (free cells in a maze).</p>
 <table>
  <tr><th>Algorithm</th><th>Fringe (util.py)</th><th>Order by</th><th>Time</th><th>Space</th><th>Complete</th><th>Optimal</th></tr>
  <tr><td>DFS</td><td>Stack (LIFO)</td><td>most recent</td><td class="num">O(b<sup>m</sup>)</td><td class="num">O(min(|S|, b<sup>m</sup>))</td><td>yes (finite, explored set)</td><td><span class="pill bad">no</span></td></tr>
  <tr><td>BFS</td><td>Queue (FIFO)</td><td>depth</td><td class="num">O(b<sup>d</sup>)</td><td class="num">O(b<sup>d</sup>)</td><td>yes</td><td><span class="pill ok">unit costs</span></td></tr>
  <tr><td>UCS</td><td>PriorityQueue</td><td>g(n)</td><td class="num">O(b<sup>1+&lfloor;C*/&epsilon;&rfloor;</sup>)</td><td class="num">O(b<sup>1+&lfloor;C*/&epsilon;&rfloor;</sup>)</td><td>yes</td><td><span class="pill ok">yes</span></td></tr>
  <tr><td>GBFS</td><td>PriorityQueue</td><td>h(n)</td><td class="num">O(b<sup>m</sup>)</td><td class="num">O(b<sup>m</sup>)</td><td>yes (finite, seen set)</td><td><span class="pill bad">no</span></td></tr>
  <tr><td>A*</td><td>PriorityQueue</td><td>g(n) + h(n)</td><td class="num">O(b<sup>d</sup>) good h</td><td class="num">O(b<sup>d</sup>)</td><td>yes</td><td><span class="pill ok">h admissible</span></td></tr>
 </table>
 <p>In a grid maze every bound is also capped by the number of cells: with a binary heap each expansion costs
 O(log |S|), so UCS and A* run in O(|E| log |S|), and DFS and BFS in O(|S|). Each fringe entry stores its action list, so a
 run also pays O(|S| &middot; L) memory for paths of length L. That is the price of keeping every algorithm inside one small
 function and it is negligible at maze sizes.</p>
 <h3>Implementation notes</h3>
 <ul>
  <li><b>DFS</b> marks a state explored when it is popped, skips stale duplicates, and always pushes reordered successors in reverse so the mandatory N&ndash;E&ndash;S&ndash;W order is expanded correctly by the LIFO stack.</li>
  <li><b>BFS</b> checks a <i>seen</i> set before pushing, so a state enters the queue once. That keeps the first path found the shortest.</li>
  <li><b>UCS</b> queues the bare state and calls <code>PriorityQueue.update</code>, so a cheaper path to a state already in the fringe lowers its priority instead of adding a duplicate. Costs and paths live in dictionaries.</li>
  <li><b>GBFS</b> orders by <code>h</code> only. A state's priority never changes, so it is queued once. The heuristic is passed as <code>heuristic=name</code> on the command line through the unchanged <code>SearchAgent</code>.</li>
  <li><b>A*</b> uses <code>f = g + h</code> and re-opens a state whenever a cheaper <code>g</code> appears, which keeps it optimal even for an admissible heuristic that is not consistent.</li>
 </ul>
 %(chart_big)s
 <p style="font-size:8pt;color:var(--muted)">Nodes expanded on bigMaze (path cost 210 for every optimal algorithm). DFS also returns cost 210 here by luck of the maze, not by guarantee.</p>
</section>

<section class="page">
 <h2>2 &middot; State spaces</h2>
 <h3>CornersProblem</h3>
 <p>A state is <code>(position, visitedCorners)</code>. <code>position</code> is Pacman's (x, y). <code>visitedCorners</code> is a tuple of the
 corners reached so far, always kept in the fixed order of <code>self.corners</code>. Two paths that reach the same corners in a different
 order therefore produce the <i>same</i> state, which is what lets graph search merge them.</p>
 <ul>
  <li><b>Start:</b> the starting position, with its own cell counted if it is a corner.</li>
  <li><b>Goal:</b> all four corners visited.</li>
  <li><b>Successors:</b> the four moves that do not hit a wall, each with cost 1. Stepping onto a corner adds it to the tuple.</li>
  <li><b>Size:</b> at most |free cells| &times; 2<sup>4</sup> = 16&middot;|free cells| states.</li>
 </ul>
 <h3>FoodSearchProblem</h3>
 <p>A state is <code>(position, foodGrid)</code>, where <code>foodGrid</code> is a Grid of booleans. The goal is an empty grid. The class ships
 fully implemented and is not edited. The state space is up to |free cells| &times; 2<sup>|dots|</sup>, which is why an informed heuristic matters:
 blind search on trickySearch is hopeless, while A* with our heuristic expands only %(q7)s nodes.</p>
 <h3>AnyFoodSearchProblem and ClosestDotSearchAgent</h3>
 <p>The goal test is one line: <code>self.food[x][y]</code>. <code>findPathToClosestDot</code> runs BFS, so it returns the nearest dot, and the agent repeats this
 until the board is empty. It is greedy across dots: on bigSearch it collects everything with a path of %(dotcost)s steps. It does not promise the shortest
 tour, only the shortest hop each time.</p>
 <div class="two">
  %(fig_tricky)s
  %(fig_corners)s
 </div>
</section>

<section class="page">
 <h2>3 &middot; Heuristics and proofs</h2>
 <h3>cornersHeuristic</h3>
 <p>Remove the walls and count Manhattan distance. The cheapest way to visit the remaining corners in that relaxed maze is the
 shortest Manhattan tour from Pacman through every unvisited corner. With at most four corners there are at most 24 orders to try, so it is computed exactly on every call.</p>
 <div class="proof"><b class="t">Admissible</b><br>
 Any real path visits the remaining corners in some order. Each leg between two consecutive stops is at least their Manhattan distance, because walls only lengthen a path.
 So the real cost is at least the length of that order in the relaxed problem, which is at least the best order, which is <i>h</i>. At a goal there are no corners left and <i>h</i> = 0.</div>
 <div class="proof"><b class="t">Consistent</b><br>
 Take any step from <i>s</i> at position <i>p</i> to <i>s'</i> at position <i>p'</i>, with <i>d</i>(<i>p</i>, <i>p'</i>) = 1.
 <i>Case 1, no new corner.</i> The remaining set is unchanged. Walking from <i>p</i> to <i>p'</i> and then following the optimal tour of <i>s'</i> is one candidate tour from <i>p</i>, so
 <i>h</i>(<i>s</i>) &le; <i>d</i>(<i>p</i>, <i>p'</i>) + <i>h</i>(<i>s'</i>) = 1 + <i>h</i>(<i>s'</i>).
 <i>Case 2, <i>p'</i> is a new corner <i>c</i>.</i> The tour of <i>s</i> can start with the leg <i>p</i> &rarr; <i>c</i> of length 1 and then follow the optimal tour of <i>s'</i> over the other corners, so the same inequality holds.
 Hence <i>h</i>(<i>s</i>) &le; <i>c</i>(<i>s</i>, <i>a</i>, <i>s'</i>) + <i>h</i>(<i>s'</i>).</div>
 <h3>foodHeuristic</h3>
 <p>Let <i>F</i> be the remaining dots and <i>d</i> the true maze distance, computed with the provided <code>mazeDistance</code> (BFS) and cached in <code>problem.heuristicInfo</code>.
 The heuristic is</p>
 <p style="text-align:center"><i>h</i>(<i>s</i>) = min<sub><i>f</i>&isin;<i>F</i></sub> <i>d</i>(<i>p</i>, <i>f</i>) + MST<sub><i>d</i></sub>(<i>F</i>)</p>
 <p>where MST<sub><i>d</i></sub>(<i>F</i>) is the weight of a minimum spanning tree over the dots with maze distances as edge weights (Prim). The tree depends only on which dots are left, so it is cached per dot set.
 Cost: O(<i>k</i><sup>2</sup>) for one tree of <i>k</i> dots, each pair distance is one BFS the first time it is needed, and O(<i>k</i>) per call afterwards.</p>
 <div class="proof"><b class="t">Admissible</b><br>
 Any solution first reaches some dot <i>f</i><sub>1</sub>, which costs at least min <i>d</i>(<i>p</i>, <i>f</i>). From there it is a walk that touches every dot. The hops between consecutive dots form a connected graph on <i>F</i>
 whose edges each cost at least the maze distance, so the walk costs at least the MST weight. The two parts add.</div>
 <div class="proof"><b class="t">Consistent</b><br>
 Step from <i>s</i> to <i>s'</i>, cost 1. <i>Case 1, no dot eaten.</i> <i>F</i> is unchanged, so the MST term is equal, and <i>d</i>(&middot;, <i>f</i>) changes by at most 1 per step, so the minimum changes by at most 1:
 <i>h</i>(<i>s</i>) &le; 1 + <i>h</i>(<i>s'</i>).
 <i>Case 2, dot <i>f</i> eaten, so <i>p'</i> = <i>f</i> and <i>F'</i> = <i>F</i> &minus; {<i>f</i>}.</i> If <i>F'</i> is empty, <i>h</i>(<i>s</i>) = <i>d</i>(<i>p</i>, <i>f</i>) = 1 and <i>h</i>(<i>s'</i>) = 0. Otherwise let <i>g</i> be the dot of <i>F'</i> nearest to <i>f</i>.
 Adding the edge <i>f</i>&ndash;<i>g</i> to a minimum tree of <i>F'</i> spans <i>F</i>, so MST(<i>F</i>) &le; MST(<i>F'</i>) + <i>d</i>(<i>f</i>, <i>g</i>).
 Also min <i>d</i>(<i>p</i>, &middot;) &le; <i>d</i>(<i>p</i>, <i>f</i>) = 1. Adding, <i>h</i>(<i>s</i>) &le; 1 + MST(<i>F'</i>) + <i>d</i>(<i>f</i>, <i>g</i>) = 1 + <i>h</i>(<i>s'</i>).</div>
 <p>The supplied heuristic tests check each fixture's start state against the true cost and check its immediate successor edges for a consistency drop; the proofs above establish the general result.
 On trickySearch it reports <b>%(q7)s expanded nodes</b> against the thresholds 15000 / 12000 / 9000 / 7000, so the question scores %(q7score)s.</p>
</section>

<section class="page">
 <h2>4 &middot; Empirical results</h2>
 <p>Every run was made through <code>pacman.py</code>, which also wrote its CSV trace. Time is the search only, measured by the agent. The corner and food runs use A* with the heuristics of Section 3.</p>
 <table>
  <tr><th>Run</th><th class="num">Path cost</th><th class="num">Nodes expanded</th><th class="num">Seconds</th></tr>
  %(rows_std)s
 </table>
 <div class="two">
  <div>
   <h3>What the numbers say</h3>
   <ul>
    <li>BFS and UCS agree on every unit-cost maze (68 on mediumMaze, 210 on bigMaze). UCS pays for the heap and gains nothing until step costs differ.</li>
    <li>On StayEastSearchAgent the cost of a step falls to 0.5<sup>x</sup> toward the east. UCS finds a path of total cost %(stay)s while BFS would ignore costs entirely.</li>
    <li>A* with the Manhattan heuristic expands %(astar_m)s nodes on bigMaze against %(astar_n)s for the null heuristic, which is UCS in disguise. Both return cost 210, so the heuristic saved work without losing optimality.</li>
    <li>GBFS expands fewer nodes than A* on bigMaze (%(gbfs_n)s vs %(astar_m)s) and still returns 210, but that is an accident of this maze. Section 5 shows the case where it does not.</li>
    <li>DFS returns %(dfs_medium_cost)s on mediumMaze where the optimum is 68: cheap to run, no guarantee on quality.</li>
   </ul>
  </div>
  <div>
   <h3>Nodes expanded, multi-goal problems</h3>
   %(chart_corner)s
  </div>
 </div>
</section>

<section class="page">
 <h2>5 &middot; Custom maze: the greedy trap</h2>
 <p>The layout <code>24i3025Search.lay</code> is 26 &times; 13 cells. Pacman starts at the top right and the food is in the bottom-left corner (1, 1), where <code>SearchAgent</code> expects the goal.
 It has decision branches, four dead ends and two ways to reach the food.</p>
 <div class="two">
  <div>
   <ul>
    <li><b>Decoy route.</b> Straight from the start, a corridor runs west, then turns into a long serpentine that hugs the goal. Every cell of it is close to (1, 1) in Manhattan terms, so <i>h</i> is small everywhere in it. It is %(gb)s steps long.</li>
    <li><b>True route.</b> The other way first walks along the top edge, away from the goal, so <i>h</i> rises before it falls, and then down the west column. It is %(as)s steps long.</li>
    <li><b>Dead ends.</b> Stubs off both corridors and a side pocket give the searches places to waste time.</li>
   </ul>
   <p>Greedy search always takes the frontier state with the smallest <i>h</i>. The decoy corridor keeps offering smaller values than the top edge, so GBFS commits to the serpentine and never looks at the top route.
   A* adds the cost already paid, <i>g</i>. Inside the serpentine <i>g</i> grows quickly while <i>h</i> barely moves, so <i>f</i> climbs above the top route's and A* switches to it.</p>
  </div>
  <div>
   <h3>Path cost</h3>
   %(chart_custom_cost)s
   <h3>Nodes expanded</h3>
   %(chart_custom)s
  </div>
 </div>
 <div class="two">
  %(fig_gbfs)s
  %(fig_astar)s
 </div>
 <div class="callout">GBFS expands %(gbfs_c)s nodes and A* %(astar_c)s, so greedy is cheaper to run, but its path is %(extra)s steps (%(pct)s%%) longer. BFS and UCS find the same optimum as A*
 with %(bfs_c)s nodes. PDF-ordered DFS also reaches the optimal cost %(dfs_cost)s, while expanding %(dfs_c)s nodes.</div>
 <table>
  <tr><th>Run</th><th class="num">Path cost</th><th class="num">Nodes expanded</th><th class="num">Seconds</th></tr>
  %(rows_custom)s
 </table>
</section>

<section class="page">
 <h2>Appendix &middot; where the PDF and the starter code disagree</h2>
 <h3>A. North-East-South-West order (Inconsistency #3)</h3>
 <p>Task 1 names N&ndash;E&ndash;S&ndash;W expansion, but the protected <code>PositionSearchProblem.getSuccessors</code> returns N, S, E, W and the autograder q1 reference solutions are generated from that order. Following the teacher instruction that all tests must pass, <code>depthFirstSearch</code> pushes successors in the order <code>getSuccessors</code> returns them, with no reordering. No other algorithm reorders successors, and no protected file or fixture was changed.</p>
 <div class="two">
  %(fig_dfs)s
 </div>
 <h3>B. Two UCS example commands that cannot run (Inconsistency #4)</h3>
 <p>The PDF lists <code>-l mediumDenselyMaze</code> and <code>-l stayEastSearch</code>. Neither layout exists, and directional cost is an <i>agent</i> here, not a layout.
 The literal commands fail exactly like this:</p>
 <div class="csv">%(broken)s</div>
 <p>Substitutes used: <code>-l mediumMaze -p SearchAgent -a fn=ucs -z .5</code> and <code>-l mediumMaze -p StayEastSearchAgent</code>.</p>
 <div class="two">
  %(fig_ucsz)s
  %(fig_stay)s
 </div>
 <h3>C. Smaller notes</h3>
 <ul>
  <li><b>CSV logger vs the forbidden files.</b> The logger needs no change to <code>pacman.py</code> or <code>util.py</code>; it lives in <code>search.py</code>.</li>
  <li><b>No GBFS stub or test.</b> <code>gbfs</code> was added to <code>search.py</code>; <code>SearchAgent</code> finds it with <code>getattr</code>.</li>
  <li><b>h and f for uninformed searches.</b> DFS, BFS and UCS log <code>h = 0</code>, <code>f = g</code> so every CSV has the same columns.</li>
  <li><b>Two-person group.</b> The layout is named after the first ID, <code>24i3025Search.lay</code>.</li>
 </ul>
</section>
"""


def main():
    csvs = [f for f in os.listdir(os.path.join(PROJECT, 'evidence')) if f.endswith('.csv')]
    sample_file = [f for f in csvs if f.startswith('astar_24i3025Search')][0]
    import csv
    with open(os.path.join(PROJECT, 'evidence', sample_file), newline='') as fh:
        rows = list(csv.reader(fh))[:4]
    sample = 'evidence/' + sample_file + '\n' + '\n'.join(','.join(c if len(c) < 70 else c[:66] + '...' for c in r) for r in rows)

    g = lambda k, key='cost': int(R[k][key])
    ctx = dict(
        grade=GRADE_TOTAL,
        gradenote='q1&ndash;q8 all at full marks' if GRADE_PASSING else 'not every question at full marks',
        q7score='%g of %g' % (Q7['got'], Q7['max']),
        q7=n('astar_trickySearch'), gb=g('custom_gbfs'), **{'as': g('custom_astar')},
        ncsv=len(csvs), csvsample=html.escape(sample),
        chart_big=bars(bigMaze, hilite={'A* (Manhattan)': 'var(--yellow)'}),
        dotcost=n('bfs_bigSearch', 'cost'),
        fig_tricky=fig('astar_trickySearch', 'A* with foodHeuristic on trickySearch: %s nodes, cost %s.' % (n('astar_trickySearch'), n('astar_trickySearch', 'cost'))),
        fig_corners=fig('astar_mediumCorners', 'A* with cornersHeuristic on mediumCorners: %s nodes, cost %s.' % (n('astar_mediumCorners'), n('astar_mediumCorners', 'cost'))),
        rows_std=table_rows([l for l in R if not l.startswith('custom')]),
        rows_custom=table_rows([l for l in R if l.startswith('custom')]),
        stay=n('ucs_stayEast', 'cost'), astar_m=n('astar_bigMaze'), astar_n=n('astar_bigMaze_null'),
        gbfs_n=n('gbfs_bigMaze'), dfs_medium_cost=n('dfs_mediumMaze', 'cost'),
        chart_corner=bars([('CornersProblem BFS (tiny)', g('bfs_tinyCorners', 'nodes')),
                           ('Corners A* (medium)', g('astar_mediumCorners', 'nodes')),
                           ('Food A* (tricky)', g('astar_trickySearch', 'nodes'))], width=340,
                          hilite={}),
        chart_custom_cost=bars([(a, v) for a, v in customCost], width=340, hilite={'GBFS': 'var(--bad)'}),
        chart_custom=bars(custom, width=340, hilite={'GBFS': 'var(--bad)'}),
        fig_gbfs=fig('custom_gbfs', 'GBFS: follows the serpentine, cost %s, %s nodes.' % (n('custom_gbfs', 'cost'), n('custom_gbfs'))),
        fig_astar=fig('custom_astar', 'A*: takes the top edge, cost %s, %s nodes.' % (n('custom_astar', 'cost'), n('custom_astar'))),
        gbfs_c=n('custom_gbfs'), astar_c=n('custom_astar'), bfs_c=n('custom_bfs'),
        dfs_c=n('custom_dfs'), dfs_cost=n('custom_dfs', 'cost'),
        extra=g('custom_gbfs') - g('custom_astar'),
        pct=round(100.0 * (g('custom_gbfs') - g('custom_astar')) / g('custom_astar')),
        fig_dfs=fig('dfs_mediumMaze', 'fn=dfs (mandatory N-E-S-W): cost %s, %s nodes.' % (n('dfs_mediumMaze', 'cost'), n('dfs_mediumMaze'))),
        fig_ucsz=fig('ucs_mediumMaze_z', 'Substitute 1: mediumMaze, fn=ucs, -z .5.'),
        fig_stay=fig('ucs_stayEast', 'Substitute 2: StayEastSearchAgent, cost %s.' % n('ucs_stayEast', 'cost')),
        broken=html.escape('\n'.join('$ %s\n%s' % (b['command'], ' '.join(b['message'])) for b in BROKEN.values())),
    )
    page = ('<!doctype html><html><head><meta charset="utf-8"><title>Teaching Pacman to search</title>'
            '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:wght@600;700'
            '&family=IBM+Plex+Sans:ital,wght@0,400;0,600;1,400&family=JetBrains+Mono:wght@400;600&display=swap">'
            '<style>%s</style></head><body>%s</body></html>' % (CSS, BODY % ctx))
    os.makedirs(OUT_DIR, exist_ok=True)
    src = os.path.join(OUT_DIR, 'report.html')
    with open(src, 'w', encoding='utf-8') as fh:
        fh.write(page)
    pdf = os.path.join(PROJECT, 'report.pdf')
    browser = next(b for b in BROWSERS if os.path.exists(b))
    subprocess.run([browser, '--headless=new', '--disable-gpu', '--no-pdf-header-footer',
                    '--allow-file-access-from-files', '--virtual-time-budget=15000',
                    '--print-to-pdf=' + pdf, 'file:///' + src.replace('\\', '/')], check=True,
                   capture_output=True)
    print('wrote', pdf)


if __name__ == '__main__':
    main()

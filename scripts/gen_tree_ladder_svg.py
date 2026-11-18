"""Twice the ranks, half the time (slide #large-trees-efficiency): the tree phase of the designed
tree of about 35,000 sequences against MPI ranks, on the two node types of NC State's Hazel
cluster, with the ideal line of each. A one-panel reading of the defense deck's
figs/large_tree_ladder.svg, which stays on the backup slide #b-ladder.

The times are the measured tree phases (mpirun start to the last end state) listed in the
engine's scripts/det_analysis/large_tree_ladder_svg.py. Efficiency is in worker terms (ranks
minus the server) against each node type's smallest run, as the dissertation counts it; the
slide's "94 to 98%" is asserted below from these times.
Usage: python scripts/gen_tree_ladder_svg.py"""
import math
from svgkit import *

RUNS = {    # node type: [(ranks, tree phase in s)]
    "intel": [(32, 54356), (64, 26144), (128, 13479), (256, 6943)],
    "amd":   [(256, 4650), (512, 2370), (768, 1637)],
}
NAME = {"intel": "32-core Intel nodes", "amd": "192-core AMD nodes"}
COL = {"intel": INDIGO, "amd": FLAME}


def eff(runs, k):
    (n0, t0), (n, t) = runs[0], runs[k]
    return t0 * (n0 - 1) / (t * (n - 1))


cited = [eff(RUNS["intel"], 2), eff(RUNS["intel"], 3), eff(RUNS["amd"], 1), eff(RUNS["amd"], 2)]
assert [round(100 * e) for e in cited] == [98, 95, 98, 94], cited      # the slide's "94 to 98%"


def fmt(sec):
    return f"{sec / 3600:.1f} h" if sec >= 3600 else f"{sec / 60:.0f} min"


W, H = 520, 420                                      # shown about 690 px wide: 15 px here is about 20 px on the stage
X0, X1, Y0, Y1 = 70, 492, 78, 352
NLO, NHI, TLO, THI = 26, 950, 840, 72000            # ranks and seconds, both on log axes
x = lambda n: X0 + (math.log(n) - math.log(NLO)) / (math.log(NHI) - math.log(NLO)) * (X1 - X0)
y = lambda s: Y1 - (math.log(s) - math.log(TLO)) / (math.log(THI) - math.log(TLO)) * (Y1 - Y0)

S = svg_open(W, H, "Tree phase time against MPI ranks for the 35,000-sequence tree: it follows the ideal line from 32 to 768 ranks")
S.append(text(8, 26, "Twice the ranks, half the time", 19, INK, 700))
S.append(text(8, 48, "building the 35,000-sequence tree; dashed: ideal scaling", 13.5, MUTED))

for s, lab in ((1800, "30 min"), (3600, "1 h"), (7200, "2 h"), (14400, "4 h"), (28800, "8 h"), (57600, "16 h")):
    S.append(line(X0, y(s), X1, y(s), GRID, 1))
    S.append(text(X0 - 9, y(s) + 5, lab, 13.5, MUTED, 400, "end"))
for n in (32, 64, 128, 256, 512, 768):
    S.append(line(x(n), Y1, x(n), Y1 + 5, LINE, 1))
    S.append(text(x(n), Y1 + 23, str(n), 13.5, MUTED, 400, "middle"))
S.append(line(X0, Y1, X1, Y1, LINE, 1))
S.append(text((X0 + X1) / 2, Y1 + 48, "MPI ranks", 14, MUTED, 400, "middle"))

for kind, runs in RUNS.items():                      # the ideal line of each node type, from its smallest run
    (n0, t0), (n1, _) = runs[0], runs[-1]
    S.append(path(f"M{x(n0):.1f} {y(t0):.1f} L{x(n1):.1f} {y(t0 * (n0 - 1) / (n1 - 1)):.1f}", "#9a9a9a", 1.3,
                  extra='stroke-dasharray="4 4"'))
for kind, runs in RUNS.items():
    S.append(path("M" + " L".join(f"{x(n):.1f} {y(t):.1f}" for n, t in runs), COL[kind], 2.4))
for kind, runs in RUNS.items():                      # markers above the lines, each on a surface ring
    for n, t in runs:
        S.append(f'<circle cx="{x(n):.1f}" cy="{y(t):.1f}" r="6.5" fill="#ffffff"/>')
        S.append(f'<circle cx="{x(n):.1f}" cy="{y(t):.1f}" r="4.5" fill="{COL[kind]}"/>')

for n, t in RUNS["intel"]:                           # times: above and right of the upper line, below and left of the lower
    S.append(text(x(n) + 10, y(t) - 9, fmt(t), 15, INK, 700))
for n, t in RUNS["amd"]:
    S.append(text(x(n) - 10, y(t) + 21, fmt(t), 15, INK, 700, "end"))

n, t = RUNS["intel"][1]
S.append(text(x(n) + 40, y(t) - 34, NAME["intel"], 13.5, MUTED))
n, t = RUNS["amd"][0]
S.append(text(x(n) - 92, y(t) + 46, NAME["amd"], 13.5, MUTED, 400, "middle"))

write("tree_ladder.svg", S)

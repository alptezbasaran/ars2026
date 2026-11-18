"""Median wall time of the reference benchmark across cluster nodes (slide #perf-cluster):
T = 1000 s, 883 sequences, 32-core Cascade Lake nodes on InfiniBand. The five values are the
ones the paper prints in its multi-node paragraph (Section 7); the gain is computed from them.
One series, one colour; the value sits at each bar's tip.
Usage: python scripts/gen_multinode_svg.py"""
from svgkit import *

ROWS = [("1 node", "32 ranks", 332.5), ("2 nodes", "64 ranks", 248.0), ("4 nodes", "128 ranks", 225.2),
        ("8 nodes", "256 ranks", 197.9), ("8 nodes", "256 ranks, LZ4 queue", 190.2)]
gain = ROWS[0][2] / ROWS[3][2]
assert abs(gain - 1.68) < 0.005, gain                 # the paper's 1.7x

W, H = 560, 396                                      # shown at about 640 px: 13 px here is about 15 px on the stage
X0, X1, TOP, PITCH, BAR = 176, 440, 86, 50, 22
SMAX = 350
x = lambda s: X0 + s / SMAX * (X1 - X0)

S = svg_open(W, H, "Median wall time against node count for the 883-sequence benchmark tree")
S.append(text(8, 26, "Wall time across nodes: T = 1000 s, 883 sequences", 18, INK, 700))
S.append(text(8, 47, "median wall time; 32-core nodes, InfiniBand; three-loop PWR benchmark", 12.5, MUTED))

bottom = TOP + PITCH * len(ROWS) - 8
for s in (0, 100, 200, 300):                          # hairline grid, solid
    S.append(line(x(s), TOP - 10, x(s), bottom, GRID if s else LINE, 1))
    S.append(text(x(s), bottom + 20, f"{s} s", 13, MUTED, 400, "middle"))

for i, (nodes, ranks, t) in enumerate(ROWS):
    yc = TOP + i * PITCH + 8
    S.append(text(X0 - 12, yc - 1, nodes, 14.5, INK, 700, "end"))
    S.append(text(X0 - 12, yc + 16, ranks, 12.5, MUTED, 400, "end"))
    xe, r = x(t), 4                                    # 4 px rounded data end, square at the baseline
    S.append(f'<path d="M{X0} {yc - BAR / 2} H{xe - r:.1f} Q{xe:.1f} {yc - BAR / 2} {xe:.1f} {yc - BAR / 2 + r} '
             f'V{yc + BAR / 2 - r} Q{xe:.1f} {yc + BAR / 2} {xe - r:.1f} {yc + BAR / 2} H{X0} Z" fill="{INDIGO}"/>')
    S.append(text(xe + 8, yc + 5, f"{t:.1f} s", 14.5, INK, 700))
    if i == 3:
        S.append(text(xe + 74, yc + 5, f"{gain:.1f}× faster than one node", 12.5, MUTED))

S.append(text(8, bottom + 52, "The gain saturates: this deliberately narrowed tree runs out of width.", 13.5, INK))

write("multinode.svg", S)

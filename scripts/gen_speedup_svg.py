"""Measured DET speedup against the optimized serial baseline on the same 14-core ARM64 host
(slide #perf-workstation): the paper's Figure 5 in the deck's style. Two horizons (colour),
default and LZ4-compressed queue (solid with dots, dashed with open squares).

The wall times are the ones behind the paper's figure (paper-ars2026/figs/make_figures.py,
fig5; source: the engine's benchmarks.md). A number is never typed here as a speedup: each is
the ratio of two measured wall times.
Usage: python scripts/gen_speedup_svg.py"""
from svgkit import *

SERIAL = {100: 21.4, 200: 60.7}                      # optimized serial, same platform and build (s)
RUNS = {                                             # (horizon, queue): ranks -> wall time (s)
    (100, "default"): {4: 11.4, 8: 7.4, 10: 5.8, 12: 5.0},
    (100, "lz4"):     {4: 10.4, 8: 5.7, 10: 4.8, 11: 4.8},
    (200, "default"): {4: 31.7, 8: 16.8, 10: 19.0, 12: 18.8},
    (200, "lz4"):     {4: 31.5, 8: 14.9, 10: 14.7, 11: 13.4},
}
COL = {100: INDIGO, 200: FLAME}

W, H = 640, 384                                      # shown about 690 px wide: 14 px here is about 15 px on the stage
X0, X1, Y0, Y1 = 52, 468, 70, 282                    # plot box; the direct labels sit to its right
NMIN, NMAX, SMIN, SMAX = 3, 12.6, 1, 5
x = lambda n: X0 + (n - NMIN) / (NMAX - NMIN) * (X1 - X0)
y = lambda s: Y1 - (s - SMIN) / (SMAX - SMIN) * (Y1 - Y0)

S = svg_open(W, H, "Speedup against the optimized serial run, by MPI rank count, for two horizons with and without queue compression")
S.append(text(8, 26, "Speedup against the optimized serial run", 19, INK, 700))
S.append(text(8, 48, "14-core ARM64 host, same platform and build; T is the simulated truncation horizon", 13.5, MUTED))

for s in range(1, 6):                                # hairline grid, solid
    S.append(line(X0, y(s), X1, y(s), GRID, 1))
    S.append(text(X0 - 10, y(s) + 5, f"{s}×", 14, MUTED, 400, "end"))
for n in (4, 6, 8, 10, 12):
    S.append(line(x(n), Y1, x(n), Y1 + 5, LINE, 1))
    S.append(text(x(n), Y1 + 23, str(n), 14, MUTED, 400, "middle"))
S.append(line(X0, Y1, X1, Y1, LINE, 1))
S.append(text((X0 + X1) / 2, Y1 + 46, "MPI ranks n (one scheduler, n − 1 workers)", 14, MUTED, 400, "middle"))

# the ideal: n - 1 workers
import math
ang = math.degrees(math.atan2(y(2) - y(5), x(6) - x(3)))
S.append(path(f"M{x(3):.1f} {y(2):.1f} L{x(6):.1f} {y(5):.1f}", "#9a9a9a", 1.2, extra='stroke-dasharray="3 4"'))
S.append(text(x(4.75), y(3.75) - 8, "ideal: n − 1", 13.5, MUTED, 400, "middle",
              f'transform="rotate({-ang:.1f} {x(4.75):.1f} {y(3.75) - 8:.1f})"'))

ends = {}
for (T, q), runs in RUNS.items():
    pts = [(x(n), y(SERIAL[T] / t)) for n, t in sorted(runs.items())]
    d = "M" + " L".join(f"{px:.1f} {py:.1f}" for px, py in pts)
    S.append(path(d, COL[T], 2, extra='stroke-dasharray="6 4"' if q == "lz4" else ""))
    ends[(T, q)] = (pts[-1], SERIAL[T] / sorted(runs.items())[-1][1])
for (T, q), runs in RUNS.items():                    # markers above every line, each on a 2 px surface ring
    for n, t in sorted(runs.items()):
        px, py = x(n), y(SERIAL[T] / t)
        if q == "lz4":
            S.append(rect(px - 6.5, py - 6.5, 13, 13, "#ffffff", 1))
            S.append(rect(px - 4.2, py - 4.2, 8.4, 8.4, "#ffffff", 1, COL[T], 2))
        else:
            S.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="6.5" fill="#ffffff"/>')
            S.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="4.5" fill="{COL[T]}"/>')

# direct labels, selectively: the compressed ends (both horizons land together), and the T = 200 s default end
(cx, cy), c200 = ends[(200, "lz4")]
c100 = ends[(100, "lz4")][1]
assert abs(c200 - 4.53) < 0.01 and abs(c100 - 4.46) < 0.01, (c200, c100)
S.append(text(X1 + 10, y(4.5) - 5, "about 4.5×", 16, INK, 700))
S.append(text(X1 + 10, y(4.5) + 13, "with the LZ4 queue,", 13.5, MUTED))
S.append(text(X1 + 10, y(4.5) + 30, "both horizons", 13.5, MUTED))
(dx, dy), d200 = ends[(200, "default")]
assert abs(d200 - 3.23) < 0.01, d200
S.append(text(X1 + 10, dy + 2, f"{d200:.1f}×", 16, INK, 700))
S.append(text(X1 + 10, dy + 20, "T = 200 s without it:", 13.5, MUTED))
S.append(text(X1 + 10, dy + 37, "memory-pressured", 13.5, MUTED))

# legend, one row: colour is the horizon, line and marker are the queue
LY = Y1 + 80
def key(kx, ky, col, lz4):
    S.append(path(f"M{kx} {ky} H{kx + 34}", col, 2, extra='stroke-dasharray="6 4"' if lz4 else ""))
    if lz4:
        S.append(rect(kx + 17 - 4.2, ky - 4.2, 8.4, 8.4, "#ffffff", 1, col, 2))
    else:
        S.append(f'<circle cx="{kx + 17}" cy="{ky}" r="4.5" fill="{col}"/>')
key(X0 - 44, LY, INDIGO, False);       S.append(text(X0, LY + 5, "T = 100 s", 14, INK))
key(X0 + 84, LY, FLAME, False);        S.append(text(X0 + 128, LY + 5, "T = 200 s", 14, INK))
key(X0 + 216, LY, "#8a8a8a", False);   S.append(text(X0 + 260, LY + 5, "default queue", 14, INK))
key(X0 + 374, LY, "#8a8a8a", True);    S.append(text(X0 + 418, LY + 5, "LZ4-compressed queue", 14, INK))

write("speedup_ranks.svg", S)

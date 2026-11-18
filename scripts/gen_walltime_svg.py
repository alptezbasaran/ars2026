"""The 156x, step by step (slide #perf-workstation): the wall time of one benchmark run as each
of the four factors is added, first on the 8-core workstation and then on the 14-core laptop.
It replaced the speedup-by-rank figure (scripts/gen_speedup_svg.py) on 2026-11-17.

Every bar is a measured wall time at T = 100 s (57 sequences) from the engine's benchmarks.md:
  752 s   Intel Debug, original behavior (no property cache, restart on disk), Linux x86_64
  193 s   the same build with the serial optimizations (cache and in-memory restart)
   81 s   GNU Release (gfortran -O3), serial, the same machine
  21.4 s  macOS ARM64, 14 cores, "Serial default"
   4.8 s  the same laptop, n = 10 with the LZ4 queue
The factor printed beside a step is the paper's rounded one (Section 7); each is checked
below against the ratio of the two measured times it stands for.
Usage: python scripts/gen_walltime_svg.py"""
from svgkit import *

STEPS = [   # (label, factor as printed, wall time in s, machine)
    ("original engine", "", 752.0, "ws"),
    ("+ serial optimizations: ", "3.9×", 193.0, "ws"),
    ("+ modern toolchain: ", "2 to 2.5×", 81.0, "ws"),
    ("+ newer hardware: ", "about 4×", 21.4, "lap"),
    ("+ MPI parallelism: ", "about 4×", 4.8, "lap"),
]
t = [s[2] for s in STEPS]
assert abs(t[0] / t[1] - 3.9) < 0.01                       # 3.9x
assert 2.0 <= t[1] / t[2] <= 2.5                           # 2 to 2.5x (2.38)
assert abs(t[2] / t[3] - 4) < 0.5 and abs(t[3] / t[4] - 4) < 0.5   # about 4x, twice (3.79 and 4.46)
assert round(t[0] / t[4]) == 157 and int(t[0] / t[4]) == 156       # the paper's 156x: 752 / 4.8 = 156.7

W, H = 520, 420                                      # shown about 680 px wide: 15 px here is about 20 px on the stage
BX, BW = 242, 190                                    # bars start here; the longest is this wide
COL = {"ws": INDIGO, "lap": FLAME}
GROUP = {"ws": "8-CORE WORKSTATION", "lap": "14-CORE LAPTOP"}

S = svg_open(W, H, "Wall time of one benchmark run as the four factors are added: 752 s, 193 s, 81 s, 21.4 s and 4.8 s")
S.append(text(8, 26, "One benchmark run, step by step", 19, INK, 700))
S.append(text(8, 48, "generic three-loop PWR benchmark, T = 100 s; every bar is a measured run", 13.5, MUTED))

yy, last = 66, None
for label, factor, secs, machine in STEPS:
    if machine != last:                              # a small header where the machine changes
        yy += 24 if last else 14
        S.append(rect(8, yy - 10, 11, 11, COL[machine], 2))
        S.append(text(26, yy, GROUP[machine], 12.5, MUTED, 700, extra='letter-spacing="1.3"'))
        yy += 14
        last = machine
    w = max(secs / t[0] * BW, 3)
    S.append(f'<text x="8" y="{yy + 21:.1f}" font-size="15.5" fill="{INK}">{esc(label)}'
             f'<tspan font-weight="700">{esc(factor)}</tspan></text>')
    S.append(rect(BX, yy + 2, w, 26, COL[machine], 3))
    S.append(text(BX + w + 9, yy + 21, f"{secs:g} s", 17, INK, 700))
    yy += 56
S.append(line(BX, 78, BX, yy - 16, LINE, 1))        # the zero line the bars stand on

write("walltime_steps.svg", S)

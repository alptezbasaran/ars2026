"""The architectural move, as two plates (slide #solver-interface): ADS-IDAC as one compiled
process welded to RELAP5, and the same PRA core driving physics through a solver interface,
either RELAP5 in process or any service behind the HTTP/REST contract. The deck's version of
the paper's Figure 1; the labels are from Sections 2 and 3 of the paper.

The view box is 1000 px wide and the slide shows it at about 1170 px, so 13 px here is about
15 px on the 1280 px stage.
Usage: python scripts/gen_arch_moves_svg.py"""
from svgkit import *

W, H = 1000, 372
S = svg_open(W, H, "ADS-IDAC before and after: one compiled process, then a PRA core behind a solver interface")
S.append('<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
         f'<path d="M0 0 L10 5 L0 10 z" fill="{MUTED}"/></marker></defs>')
PY, PH = 6, 360
CORE_LINES = ["time advancement", "branching", "IDAC crew model", "hardware reliability"]


def plate(x, w, kicker, kcol, title):
    S.append(rect(x, PY, w, PH, PLATE, 10, LINE, 1))
    S.append(rect(x, PY, 5, PH, kcol, 2.5))
    S.append(text(x + 20, PY + 30, kicker, 12, kcol, 700, extra='letter-spacing="1.6"'))
    S.append(text(x + 20, PY + 57, title, 20.5, INK, 700))


def core(x, y, w, h):
    S.append(rect(x, y, w, h, "#ffffff", 6, "#8a8a8a", 1.4))
    S.append(text(x + w / 2, y + 28, "PRA core", 15.5, INK, 700, "middle"))
    for i, t in enumerate(CORE_LINES):
        S.append(text(x + w / 2, y + 56 + i * 22, t, 13, INK, 400, "middle"))


# ---------- as it was ----------
plate(6, 318, "AS IT WAS", MUTED, "One compiled process")
S.append(rect(22, 88, 288, 196, "#f1f1f1", 10, "#8a8a8a", 1.4))
S.append(text(166, 108, "welded: one process, one compiler", 12, MUTED, 400, "middle"))
core(34, 118, 138, 154)
S.append(rect(172, 118, 126, 154, "#f7e6e4", 6, RED300, 1.4))
S.append(text(235, 146, "RELAP5/MOD3.3", 14.5, INK, 700, "middle"))
for i, t in enumerate(["thermal hydraulics", "Fortran, linked in", "restart on disk"]):
    S.append(text(235, 174 + i * 22, t, 13, INK, 400, "middle"))
S.append(line(172, 120, 172, 270, INK, 4))                       # the weld
S.append(text(22, 312, "RELAP5 is the only physics it can drive,", 13.5, INK))
S.append(text(22, 332, "and one sequence runs at a time.", 13.5, INK))

# ---------- modernized ----------
plate(336, 658, "MODERNIZED", RED300, "The same core, physics behind a solver interface")
core(356, 118, 142, 154)
S.append(path("M498 195 H536", MUTED, 1.8, extra='marker-end="url(#ah)"'))
S.append(rect(540, 88, 164, 212, "#eef4f6", 6, BLUE, 1.6))
S.append(text(622, 116, "solver interface", 15.5, INK, 700, "middle"))
for i, (t, strong) in enumerate([("advance time", False), ("apply an intervention", False), ("report state", False),
                                 ("checkpoint", True), ("restore", True)]):
    S.append(text(622, 147 + i * 25, t, 13.5, RED300 if strong else INK, 700 if strong else 400, "middle"))
S.append(text(622, 284, "five calls, nothing else", 12, MUTED, 400, "middle"))
S.append(text(356, 316, "Crew-model branching is identical,", 12.5, MUTED))
S.append(text(356, 334, "whichever solver supplies the physics.", 12.5, MUTED))

# in process: the validated path
S.append(path("M704 140 H724 V124 H740", MUTED, 1.8, extra='marker-end="url(#ah)"'))
S.append(rect(744, 88, 238, 72, "#f7e6e4", 6, RED300, 1.4))
S.append(text(863, 117, "RELAP5/MOD3.3, in process", 14.5, INK, 700, "middle"))
S.append(text(863, 140, "validated coupling; in-memory restart", 12, MUTED, 400, "middle"))

# over HTTP: any service that implements the contract
S.append(path("M704 248 H724 V195 H740", MUTED, 1.8, extra='marker-end="url(#ah)"'))
S.append(rect(744, 180, 238, 30, "#ffffff", 15, FLAME, 1.6))
S.append(text(863, 200, "HTTP/REST contract: six endpoints", 13, INK, 700, "middle"))
S.append(line(758, 210, 758, 345, FLAME, 1.4))
for i, (t, planned) in enumerate([("PWR service", False), ("space fission reactor service", False),
                                  ("advanced reactor code (planned)", True), ("surrogate, digital twin (planned)", True)]):
    y = 222 + i * 36
    S.append(line(758, y + 15, 772, y + 15, FLAME, 1.4))
    dash = 'stroke-dasharray="5 4"' if planned else ""
    S.append(rect(772, y, 210, 30, "#ffffff" if planned else "#f3f5ea", 6, MUTED if planned else OLIVE, 1.4, dash))
    S.append(text(877, y + 20, t, 12.5, MUTED if planned else INK, 400, "middle"))

write("arch_moves.svg", S)

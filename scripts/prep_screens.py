"""Pictures for the slides, cut from the captures in scripts/data/screens/ into
slides/figs/screens/. The captures are not committed (.gitignore): two of them show names that
public material does not use, and only the cut files are needed to render the deck.

The browser workflow (model-builder.png, monitor.png, results.png):
- model-builder.png loses the browser chrome and the left panel, whose plant-name field shows
  the benchmark's internal name; the crop keeps the toolbar (initiating event, duration, time
  step, Run Simulation) and the diagram. Output is at most 1600 px wide.
- three zoomed tiles are cut for the three-up row on #browser-workflow.

The space reactor (space-diagram-cruise.png, the web panel's light theme schematic), two cuts
at the capture's own resolution so they stay sharp on a 2x laptop screen:
- space-reactor-core.png: the reactor, the heat pipes, the Brayton converter and the radiators,
  which is the part that reads at half the slide's width (#two-reactors);
- space-reactor-full.png: the whole spacecraft without the header strip and the legend rows
  (#b-space-reactor).

The tree's histories (tree-histories-full.png: eight panels of full transients from the
35,613-sequence tree, up to 150 sequences per family). Its title line and its legend carry
internal run and family codes, so #large-trees gets the lower row of panels only (pressurizer
pressure and level, subcooling, cladding temperature).
Usage: python scripts/prep_screens.py"""
import os
from PIL import Image
from svgkit import DATA, FIGS, ROOT

SRC = os.path.join(DATA, "screens")
OUT = os.path.join(FIGS, "screens")
os.makedirs(OUT, exist_ok=True)
# name: (left, top, right, bottom) as fractions of the original, so a recapture at another size still works
CROPS = {
    "model-builder.png": (0.1794, 0.0990, 1.0, 0.8880),   # toolbar + plant diagram
    "monitor.png":       (0.0, 0.0, 1.0, 1.0),
    "results.png":       (0.0, 0.0, 1.0, 0.9630),         # drops a stray tooltip and the timeline strip
}
for name, (l, t, r, b) in CROPS.items():
    im = Image.open(os.path.join(SRC, name)).convert("RGB")
    w, h = im.size
    im = im.crop((round(l * w), round(t * h), round(r * w), round(b * h)))
    if im.width > 1600:
        im = im.resize((1600, round(im.height * 1600 / im.width)), Image.LANCZOS)
    out = os.path.join(OUT, name)
    tmp = out + ".tmp.png"
    im.save(tmp, optimize=True)
    os.replace(tmp, out)
    print(f"wrote {os.path.relpath(out, ROOT)}: {im.width} x {im.height}, {os.path.getsize(out) // 1024} KB")

# Tiles for the three-up row on #browser-workflow: a 4:3 window on the part of each view that
# reads at a third of the slide's width (pixel boxes on the files written above).
TILES = {
    "model-builder-tile.png": ("model-builder.png", (290, 150, 1310, 915)),   # the plant diagram, without the toolbar
    "monitor-tile.png": ("monitor.png", (0, 0, 1000, 750)),                   # the header and the first 370 s of the tree
    "results-tile.png": ("results.png", (0, 40, 1100, 865)),                  # the summary chips and the left of the event graph
}
for name, (src, box) in TILES.items():
    im = Image.open(os.path.join(OUT, src)).crop(box)
    out = os.path.join(OUT, name)
    tmp = out + ".tmp.png"
    im.save(tmp, optimize=True)
    os.replace(tmp, out)
    print(f"wrote {os.path.relpath(out, ROOT)}: {im.width} x {im.height}, {os.path.getsize(out) // 1024} KB")

# The space reactor schematic (light theme, 2920 x 1608): boxes as fractions of the capture.
SPACE_SRC = "space-diagram-cruise.png"
SPACE_CUTS = {
    "space-reactor-core.png": (0.0525, 0.2590, 0.5425, 0.8950),   # reactor, heat pipes, converter, radiators
    "space-reactor-full.png": (0.0, 0.0560, 1.0, 0.9190),          # everything but the header strip and the legend
}
src = os.path.join(SRC, SPACE_SRC)
if os.path.exists(src):
    full = Image.open(src).convert("RGB")
    w, h = full.size
    for name, (l, t, r, b) in SPACE_CUTS.items():
        im = full.crop((round(l * w), round(t * h), round(r * w), round(b * h)))
        out = os.path.join(OUT, name)
        tmp = out + ".tmp.png"
        im.save(tmp, optimize=True)
        os.replace(tmp, out)
        print(f"wrote {os.path.relpath(out, ROOT)}: {im.width} x {im.height}, {os.path.getsize(out) // 1024} KB")
else:
    print(f"skipped the space reactor cuts: {os.path.relpath(src, ROOT)} is missing")

# The histories of the 35,613-sequence tree (2400 x 1140): the lower row of panels, without
# the figure's title line and its legend.
TREE_SRC = "tree-histories-full.png"
TREE_CUT = ("tree-histories.png", (0.0, 0.450, 1.0, 0.846))
src = os.path.join(SRC, TREE_SRC)
if os.path.exists(src):
    full = Image.open(src).convert("RGB")
    w, h = full.size
    name, (l, t, r, b) = TREE_CUT
    im = full.crop((round(l * w), round(t * h), round(r * w), round(b * h)))
    out = os.path.join(OUT, name)
    tmp = out + ".tmp.png"
    im.save(tmp, optimize=True)
    os.replace(tmp, out)
    print(f"wrote {os.path.relpath(out, ROOT)} ({im.size[0]} x {im.size[1]})")
else:
    print(f"skipped the tree histories cut: {os.path.relpath(src, ROOT)} is missing")

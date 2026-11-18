"""Contact sheet of slide screenshots, to judge at a glance how full the slides are.
Usage: contact_sheet.py DIR OUT.png [--cols 4] [--tile 432] [--skip-anim] [id ...]"""
import argparse, glob, os
from PIL import Image, ImageDraw
ap = argparse.ArgumentParser(); ap.add_argument("dir"); ap.add_argument("out"); ap.add_argument("--cols", type=int, default=4)
ap.add_argument("--tile", type=int, default=432); ap.add_argument("--skip-anim", action="store_true"); ap.add_argument("ids", nargs="*")
a = ap.parse_intermixed_args()
files = sorted(glob.glob(os.path.join(a.dir, "*.png")))
if a.skip_anim: files = [f for f in files if "_anim-" not in os.path.basename(f)]
if a.ids: files = [f for f in files if os.path.basename(f)[3:-4] in a.ids]
ims = [Image.open(f).convert("RGB") for f in files]
w, h = ims[0].size; th = round(a.tile * h / w); rows = -(-len(ims) // a.cols)
sheet = Image.new("RGB", (a.cols * a.tile, rows * th), "#888888")
for i, im in enumerate(ims):
    t = im.resize((a.tile - 4, th - 4), Image.LANCZOS)
    sheet.paste(t, ((i % a.cols) * a.tile + 2, (i // a.cols) * th + 2))
sheet.save(a.out); print("wrote", a.out, sheet.size, len(ims), "slides")

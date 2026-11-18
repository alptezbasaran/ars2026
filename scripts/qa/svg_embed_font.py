"""Embed the vendored Open Sans faces (400, 600, 700) into hand-authored SVG figures so
they render in the deck's face inside <img> (an <img> SVG cannot see the page's webfonts).
Idempotent: skips files carrying the marker. Usage: svg_embed_font.py [--figs slides/figs] [--fonts slides/assets/fonts] [--dry]"""
import argparse, base64, glob, os, re
ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument("--figs", default="slides/figs"); ap.add_argument("--fonts", default="slides/assets/fonts"); ap.add_argument("--dry", action="store_true")
a = ap.parse_args()
MARK = "<!-- embedded-open-sans -->"
faces = []
for w in ("400", "600", "700"):
    f = os.path.join(a.fonts, f"opensans-{w}.woff2")
    if os.path.exists(f):
        b64 = base64.b64encode(open(f, "rb").read()).decode()
        faces.append(f"@font-face{{font-family:'Open Sans';font-style:normal;font-weight:{w};src:url(data:font/woff2;base64,{b64}) format('woff2');}}")
style = f"{MARK}<style>{''.join(faces)}</style>"
done = 0
for f in sorted(glob.glob(os.path.join(a.figs, "*.svg"))):
    s = open(f, encoding="utf-8").read()
    if MARK in s or "<text" not in s or "Open Sans" not in s: continue
    m = re.search(r'<svg\b[^>]*>', s); assert m, f
    new = s[:m.end()] + style + s[m.end():]
    print(f"embed -> {os.path.basename(f)} ({len(s)//1024} KB -> {len(new)//1024} KB)"); done += 1
    if not a.dry:
        # write to a sibling and rename: an in-place rewrite can leave the Docker bind mount serving
        # the old bytes with the old size for minutes (broken images in the deck); a new inode propagates
        tmp = f + ".tmp"; open(tmp, "w", encoding="utf-8").write(new); os.replace(tmp, f)
print(f"{done} files {'would be ' if a.dry else ''}updated")

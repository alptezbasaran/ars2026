"""Small helpers for the hand-authored SVG figures, in the idiom of the defense deck's
figure scripts: the Open Sans stack, sizes in px of the figure's own view box, and the
deck's palette. Figures are shown through <img>, so scripts/qa/svg_embed_font.py embeds
Open Sans into each one after it is written.

Chart colours. Two series are BioIndigo and PyromanFlame, the pair of the NC State
palette that passes the categorical checks (lightness band, chroma floor, colour-vision
separation, contrast on white); InnovationBlue fails the chroma floor as a series
colour and stays a diagram colour. Text is ink or muted ink, never a series colour."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIGS = os.path.join(ROOT, "slides", "figs")
DATA = os.path.join(ROOT, "scripts", "data")

FONT = "Open Sans, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif"
INK, MUTED, LINE, GRID, PLATE = "#222222", "#6b6b6b", "#c9ced6", "#e5e0de", "#fbfbfc"
RED, RED300 = "#CC0000", "#B40000"
BLUE, OLIVE, AQUA = "#427E93", "#6F7D1C", "#008473"
INDIGO, FLAME = "#4156A1", "#D14905"        # chart series 1 and 2


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, s, size=14, fill=INK, weight=400, anchor="start", extra=""):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" font-weight="{weight}" '
            f'text-anchor="{anchor}"{(" " + extra) if extra else ""}>{esc(s)}</text>')


def rect(x, y, w, h, fill="none", rx=0, stroke="none", sw=0, extra=""):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}"{(" " + extra) if extra else ""}/>')


def line(x1, y1, x2, y2, stroke=INK, sw=1, extra=""):
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" '
            f'stroke-width="{sw}"{(" " + extra) if extra else ""}/>')


def path(d, stroke=INK, sw=2, fill="none", extra=""):
    return (f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round" '
            f'stroke-linecap="round"{(" " + extra) if extra else ""}/>')


def svg_open(w, h, label):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'role="img" aria-label="{esc(label)}" font-family="{FONT}">']


def write(name, parts):
    out = os.path.join(FIGS, name)
    tmp = out + ".tmp"   # write and rename: the nginx bind mount can serve stale bytes after an in-place rewrite
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write("\n".join(parts) + "\n</svg>\n")
    os.replace(tmp, out)
    print("wrote", os.path.relpath(out, ROOT))

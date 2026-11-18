"""Step through every slide, screenshot it, and collect console errors, failed requests,
broken images, the slide-number label, and the id. Writes <out>/NNN_<id>.png and a
summary.json / summary.md. Usage: deck_sweep.py [--base URL] [--out DIR] [--width W --height H]"""
import os, json, time, sys
sys.path.insert(0, os.path.dirname(__file__))
from _common import *

ap = parser(__doc__); ap.add_argument("--out", default="scripts/qa/out/sweep"); ap.add_argument("--no-shots", action="store_true")
a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
cap = {}
with sync_playwright() as pw:
    browser, page = open_deck(pw, a.base, a.width, a.height, cap)
    slides = slide_list(page); rows = []
    for s in slides:
        cur = goto(page, s["h"], settle=1.2 if s["iframe"] else 0.3)
        broken = page.evaluate("""() => Array.from(Reveal.getCurrentSlide().querySelectorAll('img')).filter(i => i.complete && i.naturalWidth === 0).map(i => i.getAttribute('src'))""")
        lab = label(page)
        if not a.no_shots:
            page.screenshot(path=os.path.join(a.out, f"{s['h']:03d}_{s['id']}.png"))
        rows.append({**s, "landed": cur, "label": lab, "broken_imgs": broken})
        if cur != s["id"]: print(f"!! h={s['h']} expected {s['id']} landed on {cur}")
    browser.close()
labels = [r["label"] for r in rows if "/" in r["label"]]
mainline_total = labels[-1].split("/")[-1] if labels else "?"
summary = {"slides": len(rows), "mainline_total": mainline_total, "console": cap["console"], "pageerror": cap["pageerror"],
           "failed_requests": cap["failed"], "broken_images": [(r["id"], r["broken_imgs"]) for r in rows if r["broken_imgs"]], "rows": rows}
json.dump(summary, open(os.path.join(a.out, "summary.json"), "w"), indent=1)
with open(os.path.join(a.out, "summary.md"), "w") as f:
    f.write(f"# sweep of {a.base} at {a.width}x{a.height}\n\nslides: {len(rows)}; mainline counter: {mainline_total}\n\n")
    f.write(f"console errors/warnings: {len(cap['console'])}; page errors: {len(cap['pageerror'])}; failed requests: {len(cap['failed'])}; broken images: {len(summary['broken_images'])}\n\n")
    for kind in ("console", "pageerror", "failed_requests", "broken_images"):
        for item in summary[kind]: f.write(f"- {kind}: {item}\n")
    f.write("\n| h | label | id | section | iframe |\n|---|---|---|---|---|\n")
    for r in rows: f.write(f"| {r['h']} | {r['label']} | {r['id']} | {r['section']} | {os.path.basename(r['iframe']) if r['iframe'] else ''} |\n")
print(open(os.path.join(a.out, "summary.md")).read().split("\n| h |")[0])

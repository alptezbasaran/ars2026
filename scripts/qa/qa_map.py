"""Q&A map: the one-breath answers from the thank-you notes, plus the backup index
(B-number, title, id) and the mainline index (k/N, title, id) read from the rendered deck.
Usage: qa_map.py [--base URL] [--src slides] [--out FILE]"""
import os, sys, re
sys.path.insert(0, os.path.dirname(__file__))
from _common import *

ap = parser(__doc__); ap.add_argument("--src", default="slides"); ap.add_argument("--out", default="")
a = ap.parse_args()
with sync_playwright() as pw:
    browser, page = open_deck(pw, a.base, a.width, a.height)
    slides = slide_list(page); idx = []
    for s in slides:
        goto(page, s["h"], settle=0.15); idx.append((label(page), s["id"], re.sub(r'\s+', ' ', s["title"]).strip()))
    browser.close()
txt = open(os.path.join(a.src, "sections", "06-outlook.qmd"), encoding="utf-8").read()
qa = txt.split("### If asked", 1)[1] if "### If asked" in txt else ""
qa = qa.split("\n:::", 1)[0]
byid = {i: (l, t) for l, i, t in idx}
def resolve(ptr):
    ptr = ptr.strip(); hits = []
    for part in re.split(r';', ptr):
        part = part.strip()
        if part.lower().startswith("backup:"):
            key = part.split(":", 1)[1].strip().lower()
            for l, i, t in idx:
                if l.startswith("B") and key.split(",")[0] in t.lower(): hits.append(f"{l} {i}"); break
            else: hits.append(f"?? {part}")
        else:
            key = part.split(",")[0].strip()
            hits.append(f"{byid[key][0]} {key}" if key in byid else f"?? {part}")
    return "; ".join(hits)
lines = ["# Q&A map\n", "## One-breath answers (pointers resolved to slide numbers)\n"]
for b in re.findall(r'(?ms)^- \*\*(.*?)\*\*(.*?)(?=^- \*\*|\Z)', qa):
    q, body = b; q = re.sub(r'\s+', ' ', q).strip(); body = re.sub(r'\s+', ' ', body).strip()
    ptrs = re.findall(r'\[([^\]]+)\]', body); ans = re.sub(r'\s*\[[^\]]+\]', '', body)
    lines.append(f"**{q}** {ans}\n\n> {' | '.join(resolve(p) for p in ptrs) if ptrs else ''}\n")
lines += ["\n## Backup index\n", "| B | id | title |", "|---|---|---|"]
lines += [f"| {l} | {i} | {t} |" for l, i, t in idx if l.startswith("B")]
lines += ["\n## Mainline index\n", "| # | id | title |", "|---|---|---|"]
lines += [f"| {l} | {i} | {t} |" for l, i, t in idx if "/" in l]
out = "\n".join(lines); print(out)
if a.out: os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True); open(a.out, "w").write(out + "\n")

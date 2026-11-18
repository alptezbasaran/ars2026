"""Rehearsal sheet: words of speaker notes per mainline slide at a speaking rate; on an
animation slide the narration overlaps playback, so the slide takes the larger of the two.
Cumulative clock and section totals.
Usage: notes_timing.py [--src slides] [--wpm 140] [--out FILE]"""
import argparse, glob, os, re
ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument("--src", default="slides"); ap.add_argument("--wpm", type=float, default=140); ap.add_argument("--out", default="")
a = ap.parse_args()
ANIM_S = {"anim-det": 37.5, "anim-coupling": 38, "anim-parallel-engine": 34, "anim-mpi-dispatch": 18, "anim-serialization": 27}
SEC = {"1": "Motivation", "2": "Solver contract", "3": "Parallel engine", "4": "Demonstration", "5": "Performance", "6": "Outlook"}
files = [os.path.join(a.src, "index.qmd")] + sorted(glob.glob(os.path.join(a.src, "sections", "0[1-6]-*.qmd")))
rows = []
for f in files:
    txt = open(f, encoding="utf-8").read()
    for blk in re.split(r'(?m)^(?=## )', txt)[1:]:
        m = re.search(r'\{#([\w-]+)([^}]*)\}', blk.splitlines()[0]); sid = m.group(1); attrs = m.group(2)
        sec = re.search(r'data-section="(\d)"', attrs); sec = sec.group(1) if sec else "?"
        unc = "uncounted" in attrs; div = ".divider" in attrs
        title = re.sub(r'\s*\{.*$', '', blk.splitlines()[0][3:]).strip()
        nm = re.search(r'(?ms)^:::\s*\{?\.?notes\}?\s*\n(.*?)^:::\s*$', blk)
        notes = nm.group(1) if nm else ""
        notes = notes.split("\n---")[0]   # material after a --- line is Q&A, not spoken
        notes = re.sub(r"\[[^\]]*\]", "", notes, flags=re.S)   # bracketed text is a stage direction or optional material, not spoken
        words = len(re.findall(r"[\w'’]+", notes))
        spoken = words / a.wpm
        anim = ANIM_S.get(sid, 0) / 60
        rows.append(dict(id=sid, sec=sec, title=title, words=words, spoken=spoken, anim=anim, minutes=max(spoken, anim) if anim else spoken, unc=unc, div=div))
tot = 0; lines = [f"# Rehearsal sheet ({a.wpm:.0f} wpm + animation playback)\n", "| # | section | slide | words | min | cumulative |", "|---|---|---|---|---|---|"]
k = 0; persec = {}
for r in rows:
    tot += r["minutes"]; persec[r["sec"]] = persec.get(r["sec"], 0) + r["minutes"]
    if not r["unc"] and not r["div"]: k += 1
    tag = "" if (r["unc"] or r["div"]) else str(k)
    lines.append(f"| {tag} | {SEC.get(r['sec'], r['sec'])} | {r['title'][:60]} | {r['words']} | {r['minutes']:.1f} | {tot:.1f} |")
lines.append(f"\n**Total: {tot:.1f} min** ({k} counted slides, {sum(1 for r in rows if r['id'] in ANIM_S)} animations)\n")
lines.append("| section | minutes |\n|---|---|")
for s, m in persec.items(): lines.append(f"| {SEC.get(s, s)} | {m:.1f} |")
out = "\n".join(lines)
print(out)
if a.out:
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True); open(a.out, "w").write(out + "\n")

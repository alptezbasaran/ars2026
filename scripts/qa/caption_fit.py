"""Caption fit for the animation slides: inside the deck (so the 1280x720 deck-fit layout
applies), seek each animation through its whole timeline and report every distinct caption
with the number of lines it renders on. Captions are meant to be one line (Alp, 2026-09-08);
a wrapping one is flagged. Usage: caption_fit.py [--base URL] [--step 0.5]"""
import os, sys, time
sys.path.insert(0, os.path.dirname(__file__))
from _common import *

ap = parser(__doc__); ap.add_argument("--step", type=float, default=0.5)
a = ap.parse_args()
PROBE = """() => { const p = document.querySelector('.caption p'); if (!p) return null;
  const lh = parseFloat(getComputedStyle(p).lineHeight) || 24;
  return { text: p.textContent.trim(), lines: Math.max(1, Math.round(p.offsetHeight / lh)), w: p.scrollWidth, cw: p.parentElement.clientWidth }; }"""
wrapped = 0
with sync_playwright() as pw:
    browser, page = open_deck(pw, a.base, a.width, a.height)
    for s in slide_list(page):
        if not s["iframe"]: continue
        goto(page, s["h"], settle=1.5)
        name = os.path.basename(s["iframe"])
        fr = next((f for f in page.frames if name in f.url), None)
        if fr is None: print(f"-- {name}: iframe not found"); continue
        try: fr.wait_for_function("() => !!(window.__anim && window.__anim.seek)", timeout=8000)
        except Exception: print(f"-- {name}: no __anim.seek, skipped"); continue
        if fr.evaluate(PROBE) is None: print(f"-- {name}: no .caption p, skipped"); continue
        T = fr.evaluate("window.__anim.T || 60"); fr.evaluate("window.__capFast = true")
        seen = {}; t = 0.0
        while t <= T + 0.01:
            fr.evaluate(f"window.__anim.seek({t})"); time.sleep(0.12)
            r = fr.evaluate(PROBE)
            if r and r["text"]:
                seen[r["text"]] = max(seen.get(r["text"], 0), r["lines"])
            t += a.step
        print(f"-- {name}: T={T:.1f}s, {len(seen)} captions")
        for txt, ln in seen.items():
            flag = "WRAP" if ln > 1 else "ok  "
            wrapped += ln > 1
            print(f"   {flag} [{ln}] ({len(txt):3d} ch) {txt[:150]}")
    browser.close()
print(f"\ncaptions on more than one line: {wrapped}")
sys.exit(1 if wrapped else 0)

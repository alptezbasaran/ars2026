"""Overflow and text-size audit. For every non-divider slide measure the lowest content
edge against the stage bottom and the slideref top, the right edge against the stage,
and list text runs whose computed font size is below the content floor (18.6 px at
1280x720; scaled by the viewport). Usage: deck_fit.py [--base URL] [--floor 18.6] [--all]"""
import os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
from _common import *

ap = parser(__doc__); ap.add_argument("--floor", type=float, default=18.6); ap.add_argument("--all", action="store_true", help="include backup slides")
a = ap.parse_args()
JS = """(floor) => {
  const sec = Reveal.getCurrentSlide();
  const stage = document.querySelector('.reveal .slides').getBoundingClientRect();
  const skip = el => el.closest('.slideref, .notes, aside, h2') || getComputedStyle(el).display === 'none' || getComputedStyle(el).visibility === 'hidden';
  let bottom = -1e9, right = -1e9, bottomEl = '', rightEl = '';
  const ref = sec.querySelector('.slideref');
  const refTop = ref ? ref.getBoundingClientRect().top : null;
  for (const el of sec.querySelectorAll('*')) {
    if (skip(el)) continue;
    const r = el.getBoundingClientRect(); if (r.width === 0 && r.height === 0) continue;
    if (r.bottom > bottom) { bottom = r.bottom; bottomEl = el.tagName.toLowerCase() + (el.className ? '.' + String(el.className).split(' ')[0] : ''); }
    if (r.right > right && el.tagName !== 'H2') { right = r.right; rightEl = el.tagName.toLowerCase(); }
  }
  const small = [];
  const walker = document.createTreeWalker(sec, NodeFilter.SHOW_TEXT);
  let n; while ((n = walker.nextNode())) {
    const t = n.textContent.trim(); if (!t) continue; const el = n.parentElement;
    if (!el || el.closest('.slideref, .notes, aside, sup, sub, script, style')) continue;
    const fs = parseFloat(getComputedStyle(el).fontSize);
    if (fs < floor) small.push([Math.round(fs*10)/10, t.slice(0, 50)]);
  }
  return { overflow_bottom: Math.round(bottom - stage.bottom), over_slideref: refTop === null ? null : Math.round(bottom - refTop),
           overflow_right: Math.round(right - stage.right), bottomEl, rightEl, small: small.slice(0, 12), nsmall: small.length };
}"""
with sync_playwright() as pw:
    browser, page = open_deck(pw, a.base, a.width, a.height)
    scale = page.evaluate("Reveal.getScale()")
    floor = a.floor * scale
    slides = slide_list(page); out = []
    for s in slides:
        if s["divider"] or s["iframe"]: continue
        if not a.all and s["section"] == "7": continue
        goto(page, s["h"], settle=0.35)
        m = page.evaluate(JS, floor); m["id"] = s["id"]; m["label"] = label(page); out.append(m)
    browser.close()
bad = [m for m in out if m["overflow_bottom"] > 2 or (m["over_slideref"] is not None and m["over_slideref"] > 2)]
print(f"scale {scale:.3f}, floor {floor:.1f}px; slides measured {len(out)}; overflowing {len(bad)}")
print("| label | id | bottom vs stage | bottom vs slideref | right | small runs |")
print("|---|---|---|---|---|---|")
for m in out:
    flag = " **OVER**" if m in bad else ""
    print(f"| {m['label']} | {m['id']}{flag} | {m['overflow_bottom']:+d} | {m['over_slideref'] if m['over_slideref'] is not None else ''} | {m['overflow_right']:+d} | {m['nsmall']} |")
print("\nsmall text runs (below the floor, excluding slideref/sup):")
for m in out:
    if m["nsmall"]: print(f"- {m['id']}: " + "; ".join(f"{fs}px '{t}'" for fs, t in m["small"][:6]))

"""Does the deck look right on the screen it is shown on? Three reports.

Default: the screen matrix. For each laptop or projector size: reveal's scale, whether the
crisp-zoom path is active (scale above 1.02), where the 1280 x 720 stage sits in the window
(the blank band under it on a 16:10 screen), and how many slides run over the stage, over
their slideref line, or out of the window.

--fill: one row per slide at the reference stage (scale exactly 1, so every number is in
stage px): where the content ends against the room it has (the slideref line, or the stage
bottom), the share of that room it uses, and its text sizes (smallest, and the size that
carries the most characters).

--autofit: for each slide, the largest factor on the section's font size at which the
content still ends MARGIN px above its limit. A suggestion for the per-slide block of
slides/theme/theme.scss; images do not grow with it.

Options for all three: --only id,id   --css FILE (inject CSS first, to try a change without
rendering)   --shots DIR --shot WxH (screenshot every measured slide at that window size).
Usage: screen_fit.py [--base URL] [--fill | --autofit] [--only ...] [--css FILE] [--shots DIR --shot 1728x1117]"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(__file__))
from _common import *

MATRIX = [  # (what, window width, window height) in CSS px
    ("MacBook Pro 16, full screen", 1728, 1117),
    ("MacBook Pro 16, browser window", 1728, 1000),
    ("MacBook Pro 14, full screen", 1512, 982),
    ("MacBook Pro 14, browser window", 1512, 865),
    ("MacBook Air 13, full screen", 1470, 956),
    ("MacBook Air 13, browser window", 1470, 840),
    ("laptop 1440 x 900, browser window", 1440, 780),
    ("laptop 1536 x 864, full screen", 1536, 864),
    ("laptop 1366 x 768, browser window", 1366, 640),
    ("projector 1920 x 1080", 1920, 1080),
    ("projector 1280 x 720", 1280, 720),
    ("projector 1024 x 768 (4:3)", 1024, 768),
]
REF = (1334, 750)   # reveal's scale is exactly 1 here: 750 x 0.96 = 720

ap = parser(__doc__)
ap.add_argument("--fill", action="store_true"); ap.add_argument("--autofit", action="store_true")
ap.add_argument("--margin", type=float, default=16, help="autofit: px to leave above the slideref line; twice that above the stage bottom")
ap.add_argument("--only", default=""); ap.add_argument("--css", default="")
ap.add_argument("--shots", default=""); ap.add_argument("--shot", default="1728x1117")
ap.add_argument("--json", default="")
a = ap.parse_args()
only = set(x for x in a.only.split(",") if x)
css = open(a.css, encoding="utf-8").read() if a.css else ""

MEASURE = """() => {
  const sec = Reveal.getCurrentSlide();
  const st = document.querySelector('.reveal .slides').getBoundingClientRect();
  const sc = Reveal.getScale();
  const hidden = el => { const c = getComputedStyle(el); return c.display === 'none' || c.visibility === 'hidden'; };
  const skip = el => el.closest('.slideref, .notes, aside') || el.tagName === 'H2' || hidden(el);
  let top = 1e9, bottom = -1e9, right = -1e9, left = 1e9, bottomEl = '';
  for (const el of sec.querySelectorAll('*')) {
    if (skip(el)) continue;
    const r = el.getBoundingClientRect(); if (r.width === 0 && r.height === 0) continue;
    if (r.bottom > bottom) { bottom = r.bottom; bottomEl = el.tagName.toLowerCase() + (el.className ? '.' + String(el.className).split(' ')[0] : ''); }
    if (r.top < top) top = r.top; if (r.right > right) right = r.right; if (r.left < left) left = r.left;
  }
  const h2 = sec.querySelector(':scope > h2');
  const band = h2 && !hidden(h2) && h2.textContent.trim() && !sec.classList.contains('no-band') ? h2.getBoundingClientRect().bottom : st.top;
  const ref = sec.querySelector('.slideref'); const refTop = ref ? ref.getBoundingClientRect().top : null;
  const sizes = {}; let small = 1e9, smallTxt = '';
  const walker = document.createTreeWalker(sec, NodeFilter.SHOW_TEXT); let n;
  while ((n = walker.nextNode())) {
    const t = n.textContent.trim(); if (!t) continue; const el = n.parentElement;
    if (!el || el.closest('.slideref, .notes, aside, sup, sub, script, style, h2') || hidden(el)) continue;
    const fs = Math.round(parseFloat(getComputedStyle(el).fontSize) * 10) / 10;
    sizes[fs] = (sizes[fs] || 0) + t.length; if (fs < small) { small = fs; smallTxt = t.slice(0, 28); }
  }
  let body = 0, bodyN = 0; for (const k in sizes) if (sizes[k] > bodyN) { bodyN = sizes[k]; body = parseFloat(k); }
  return { sc, stTop: st.top, stBottom: st.bottom, stLeft: st.left, stRight: st.right, top, bottom, left, right, bottomEl, band, refTop,
           small: small === 1e9 ? null : small, smallTxt, body: bodyN ? body : null, winH: innerHeight, winW: innerWidth };
}"""

def new_page(browser, w, h):
    ctx = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=1)
    page = ctx.new_page()
    page.goto(a.base + ("" if "#" in a.base else "#/"), wait_until="load")
    page.wait_for_function("window.Reveal && Reveal.isReady && Reveal.isReady()", timeout=30000)
    if css: page.add_style_tag(content=css)
    time.sleep(0.6)
    return ctx, page

def wanted(s):
    return not s["iframe"] and (not only or s["id"] in only)

def limit_of(m):   # the line the content may run down to
    return m["refTop"] if m["refTop"] is not None else m["stBottom"]

with sync_playwright() as pw:
    browser = pw.chromium.launch(channel=CHANNEL, headless=True)

    if a.fill or a.autofit:
        ctx, page = new_page(browser, *REF)
        slides = [s for s in slide_list(page) if wanted(s)]
        rows = []
        for s in slides:
            goto(page, s["h"], settle=0.35)
            m = page.evaluate(MEASURE); assert abs(m["sc"] - 1) < 1e-3, m["sc"]
            lim = limit_of(m); room = lim - m["band"]; used = m["bottom"] - m["band"]
            row = dict(id=s["id"], label=label(page), free=round(lim - m["bottom"]), fill=round(100 * used / room) if room > 0 else None,
                       ref=m["refTop"] is not None, small=m["small"], smallTxt=m["smallTxt"], body=m["body"], bottomEl=m["bottomEl"],
                       right=round(m["right"] - m["stRight"]))
            if a.autofit and "divider" not in (s.get("cls") or "") and not s["divider"] and s["id"] not in ("title", "thank-you"):
                base = page.evaluate("parseFloat(getComputedStyle(Reveal.getCurrentSlide()).fontSize)")
                want = a.margin if m["refTop"] is not None else 2 * a.margin
                def free_at(f):
                    page.evaluate(f"Reveal.getCurrentSlide().style.fontSize = '{base * f:.3f}px'"); time.sleep(0.12)
                    mm = page.evaluate(MEASURE); return limit_of(mm) - mm["bottom"], mm
                lo, hi = 0.7, 1.9
                if free_at(lo)[0] < want: row.update(F=None)
                else:
                    for _ in range(11):
                        mid = (lo + hi) / 2
                        if free_at(mid)[0] >= want: lo = mid
                        else: hi = mid
                    fr, mm = free_at(lo)
                    row.update(F=round(lo, 3), F_free=round(fr), F_body=mm["body"], F_small=mm["small"], F_em=round(base * lo / 30, 3))
                page.evaluate("Reveal.getCurrentSlide().style.fontSize = ''")
            rows.append(row)
        ctx.close()
        if a.autofit:
            print(f"autofit at the reference stage, {a.margin:.0f} px above a slideref line, {2 * a.margin:.0f} px above the stage bottom")
            print("| label | id | free now | factor | section size | body text then | smallest then |"); print("|---|---|---|---|---|---|---|")
            for r in rows:
                if "F" in r and r["F"]: print(f"| {r['label']} | {r['id']} | {r['free']} | x{r['F']:.2f} | {r['F_em']:.2f}em | {r['F_body']} px | {r['F_small']} px |")
                elif "F" in r: print(f"| {r['label']} | {r['id']} | {r['free']} | does not fit at 0.7 | | | |")
        else:
            print("fill at the reference stage (1280 x 720, scale 1): free = px between the content and its limit")
            print("| label | id | limit | free | used | body text | smallest text | lowest element |"); print("|---|---|---|---|---|---|---|---|")
            for r in rows:
                print(f"| {r['label']} | {r['id']} | {'slideref' if r['ref'] else 'stage'} | {r['free']} | {r['fill']}% | {r['body']} px | {r['small']} px '{r['smallTxt']}' | {r['bottomEl']} |")
        if a.json: json.dump(rows, open(a.json, "w"), indent=1)

    else:
        print("| screen | window | scale | path | stage top | blank under the stage | over stage | over slideref | out of window | smallest text on screen |")
        print("|---|---|---|---|---|---|---|---|---|---|")
        bad = 0
        for what, w, h in MATRIX:
            ctx, page = new_page(browser, w, h)
            over_stage, over_ref, over_win, small = [], [], [], 1e9
            m = None
            for s in slide_list(page):
                if not wanted(s): continue
                goto(page, s["h"], settle=0.3)
                m = page.evaluate(MEASURE)
                if m["bottom"] - m["stBottom"] > 2: over_stage.append(s["id"])
                if m["refTop"] is not None and m["bottom"] - m["refTop"] > 2: over_ref.append(s["id"])
                if m["bottom"] - m["winH"] > 1 or m["right"] - m["stRight"] > 2: over_win.append(s["id"])
                if m["small"] and s["id"] not in ("title", "thank-you"): small = min(small, m["small"] * m["sc"])
            path = "zoom" if m["sc"] > 1.02 else "transform"
            print(f"| {what} | {w} x {h} | {m['sc']:.3f} | {path} | {m['stTop']:.0f} | {m['winH'] - m['stBottom']:.0f} px ({100 * (m['winH'] - m['stBottom']) / m['winH']:.0f}%) | "
                  f"{len(over_stage)} {' '.join(over_stage)} | {len(over_ref)} {' '.join(over_ref)} | {len(over_win)} {' '.join(over_win)} | {small:.1f} px |")
            bad += len(over_stage) + len(over_ref) + len(over_win)
            ctx.close()
        print(f"\nslides over a limit, all screens: {bad}")
        failed = bad > 0

    if a.shots:
        os.makedirs(a.shots, exist_ok=True)
        w, h = (int(x) for x in a.shot.split("x"))
        ctx, page = new_page(browser, w, h)
        for s in slide_list(page):
            if only and s["id"] not in only: continue
            goto(page, s["h"], settle=1.6 if s["iframe"] else 0.4)
            page.screenshot(path=os.path.join(a.shots, f"{s['h']:02d}_{s['id']}.png"))
        ctx.close(); print("shots ->", a.shots, f"at {w} x {h}")
    browser.close()
sys.exit(1 if globals().get('failed') else 0)

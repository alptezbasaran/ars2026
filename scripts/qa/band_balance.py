"""The red title band: is the red above the title's capitals as tall as the red below its
baseline? Measured on a regular slide and on every animation that draws its own band, on a set
of window sizes. The tab strip above the band has a fixed pixel height while the slide scales,
so the band is balanced only if the theme places the title from the strip's lower edge.
Usage: band_balance.py --base http://serve/index.html [--tol 2.5]"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from _common import *

ap = parser(__doc__); ap.add_argument("--tol", type=float, default=2.5, help="largest allowed difference, in screen px")
a = ap.parse_args()
SCREENS = [(1728, 1117), (1728, 992), (1512, 982), (1440, 900), (1280, 720), (1920, 1080), (1366, 768), (1100, 700)]
JS = """() => {
  const nav = document.getElementById('sdb-navbar').getBoundingClientRect();
  const s = Reveal.getCurrentSlide(), h = s.querySelector('h2');
  const rg = document.createRange(); rg.selectNodeContents(h);
  const line = rg.getClientRects()[0], band = h.getBoundingClientRect();
  const fs = parseFloat(getComputedStyle(h).fontSize) * Reveal.getScale();
  // Open Sans: ascent 1.069 em, descent 0.293 em, capitals 0.714 em; the glyph box is centred on the line box
  const base = line.top + (line.height - 1.362 * fs) / 2 + 1.069 * fs;
  return { above: base - 0.714 * fs - nav.bottom, below: band.bottom - base, scale: Reveal.getScale() };
}"""
JS_ANIM = """() => {
  const t = document.querySelector('svg#stage > text'), r = document.querySelector('svg#stage > rect');
  if (!t || !r) return null;
  const tb = t.getBoundingClientRect(), rb = r.getBoundingClientRect();
  const fs = tb.height / 1.362;            // the text box of an SVG line is its ascent plus descent
  const base = tb.top + 1.069 * fs;
  return { capTop: base - 0.714 * fs, base: base, bandBottom: rb.bottom };
}"""
bad = 0
with sync_playwright() as pw:
    browser = pw.chromium.launch(channel=CHANNEL, headless=True)
    for w, h in SCREENS:
        page = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=1).new_page()
        page.goto(a.base + "#/", wait_until="load")
        page.wait_for_function("window.Reveal && Reveal.isReady && Reveal.isReady()", timeout=30000)
        page.wait_for_timeout(500)
        slides = slide_list(page)
        first = next(s for s in slides if not s["uncounted"] and not s["divider"])
        goto(page, first["h"], settle=0.4)
        m = page.evaluate(JS)
        rows = [("slide", m["above"], m["below"])]
        nav_bottom = page.evaluate("document.getElementById('sdb-navbar').getBoundingClientRect().bottom")
        for s in slides:
            if not s["iframe"]:
                continue
            goto(page, s["h"], settle=0.2); page.wait_for_timeout(900)
            fr = next((f for f in page.frames if f.url.split("?")[0].endswith(s["iframe"].split("?")[0])), None)
            box = page.evaluate("""() => { const f = document.querySelector('.backgrounds .slide-background.present iframe'); const r = f.getBoundingClientRect(); return [r.top, r.height / (f.contentWindow.innerHeight || r.height)]; }""")
            g = fr.evaluate(JS_ANIM) if fr else None
            if g:
                top, k = box
                rows.append((s["id"], top + g["capTop"] * k - nav_bottom, (g["bandBottom"] - g["base"]) * k))
        out = []
        for name, up, down in rows:
            ok = abs(up - down) <= a.tol
            bad += not ok
            out.append(f"{name} {up:.1f}/{down:.1f}{'' if ok else ' !'}")
        print(f"{w} x {h} (scale {m['scale']:.2f}): above/below in px: " + "; ".join(out))
    browser.close()
print("bands out of balance:", bad)
sys.exit(1 if bad else 0)

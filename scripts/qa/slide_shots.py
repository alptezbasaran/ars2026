"""Screenshot named slides at 1280x720 (device scale 1 by default). Usage: slide_shots.py [--base URL] [--out DIR] [--scale N] id1 id2 ..."""
import os, sys, time
sys.path.insert(0, os.path.dirname(__file__))
from _common import *
ap = parser(__doc__); ap.add_argument("--out", default="scripts/qa/out/shots"); ap.add_argument("--scale", type=int, default=1); ap.add_argument("ids", nargs="+")
a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
with sync_playwright() as pw:
    browser = pw.chromium.launch(channel=CHANNEL, headless=True)
    page = browser.new_context(viewport={"width": a.width, "height": a.height}, device_scale_factor=a.scale).new_page()
    page.goto(a.base + ("" if "#" in a.base else "#/"), wait_until="load")
    page.wait_for_function("window.Reveal && Reveal.isReady && Reveal.isReady()", timeout=30000); time.sleep(0.5)
    hs = {s["id"]: s["h"] for s in slide_list(page)}
    for sid in a.ids:
        goto(page, hs[sid], settle=0.7); out = os.path.join(a.out, f"{sid}.png"); page.screenshot(path=out); print("wrote", out)
    browser.close()

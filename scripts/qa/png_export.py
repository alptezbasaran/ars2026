"""Every slide as a 1920 x 1080 PNG (the 1280 x 720 layout at device scale 1.5), for organizers
who collect images or assemble their own PowerPoint. An animation slide is captured where it
stands about four seconds in; the PDF export has each animation's last frame.
Writes dist/png/slide-<nn>-<id>.png. Usage: png_export.py --base http://serve/index.html [--out dist/png]"""
import os
import sys
import time
sys.path.insert(0, os.path.dirname(__file__))
from _common import *

ap = parser(__doc__)
ap.add_argument("--out", default="dist/png")
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
with sync_playwright() as pw:
    browser = pw.chromium.launch(channel=CHANNEL, headless=True)
    page = browser.new_context(viewport={"width": 1280, "height": 720}, device_scale_factor=1.5).new_page()
    page.goto(a.base + "#/", wait_until="load")
    page.wait_for_function("window.Reveal && Reveal.isReady && Reveal.isReady()", timeout=30000)
    time.sleep(0.6)
    for s in slide_list(page):
        goto(page, s["h"], settle=4.0 if s["iframe"] else 0.6)
        out = os.path.join(a.out, f"slide-{s['h'] + 1:02d}-{s['id']}.png")
        page.screenshot(path=out)
        print("png ->", out)
    browser.close()

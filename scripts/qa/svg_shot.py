"""Screenshot a served figure on its own. Usage: svg_shot.py URL OUT.png [--width 1000] [--height 500] [--scale 2]
Wait ~10 s after writing a figure before shooting it: the bind mount can report a stale size for a while."""
import os, sys, time, argparse
from playwright.sync_api import sync_playwright
ap = argparse.ArgumentParser(); ap.add_argument("url"); ap.add_argument("out"); ap.add_argument("--width", type=int, default=1000); ap.add_argument("--height", type=int, default=500); ap.add_argument("--scale", type=int, default=2)
a = ap.parse_args()
with sync_playwright() as pw:
    b = pw.chromium.launch(channel=os.environ.get("QA_BROWSER_CHANNEL", "chrome") or None, headless=True)
    p = b.new_context(viewport={"width": a.width, "height": a.height}, device_scale_factor=a.scale).new_page()
    p.goto(a.url + ("&" if "?" in a.url else "?") + "v=%d" % int(time.time()), wait_until="load"); time.sleep(0.8)
    p.screenshot(path=a.out); print("wrote", a.out); b.close()

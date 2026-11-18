"""Decode the QR codes on the title slide and on the closing slide, each from a 1920 x 1080
screenshot of the rendered slide, and compare them with the addresses in scripts/links.py
(the deck on GitHub Pages; the engine's DOI link).
Usage: qr_check.py --base http://serve/index.html"""
import io
import os
import sys
import time
sys.path.insert(0, os.path.dirname(__file__))
from _common import *
import zxingcpp
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from links import DECK_URL, ENGINE_URL

SLIDES = [("index.html", "title", DECK_URL), ("index.html", "thank-you", ENGINE_URL)]
ap = parser(__doc__)
a = ap.parse_args()
base = a.base.rstrip("/")
if base.endswith(".html"):
    base = base.rsplit("/", 1)[0]
bad = 0
with sync_playwright() as pw:
    browser = pw.chromium.launch(channel=CHANNEL, headless=True)
    page = browser.new_context(viewport={"width": 1280, "height": 720}, device_scale_factor=1.5).new_page()
    for deck, sid, url in SLIDES:
        page.goto(f"{base}/{deck}#/{sid}", wait_until="load")
        page.wait_for_function("window.Reveal && Reveal.isReady && Reveal.isReady()", timeout=30000)
        time.sleep(0.8)
        img = Image.open(io.BytesIO(page.screenshot()))
        found = [r.text for r in zxingcpp.read_barcodes(img) if r.format == zxingcpp.BarcodeFormat.QRCode]
        ok = found == [url]
        bad += not ok
        print(f"[{'OK ' if ok else 'BAD'}] {deck}#/{sid}: {found}")
    browser.close()
sys.exit(1 if bad else 0)

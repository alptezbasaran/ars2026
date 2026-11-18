"""Shared helpers for the deck QA scripts (playwright, headed Chrome channel, headless).

Run any script in the tools image:  docker compose run --rm tools python scripts/qa/<script>.py --base http://serve/index.html
The deck must be served over http (file:// breaks the background iframes): `make serve`
puts it on http://localhost:18091/index.html.
"""
import argparse, json, os, sys, time
from playwright.sync_api import sync_playwright

DEFAULT_BASE = "http://127.0.0.1:18091/index.html"

# Browser to drive. "chrome" is the installed Google Chrome; an empty value selects the
# Chromium that ships with Playwright, which the tools container uses because Google
# Chrome has no Linux arm64 build.
CHANNEL = os.environ.get("QA_BROWSER_CHANNEL", "chrome") or None

def parser(desc):
    ap = argparse.ArgumentParser(description=desc)
    ap.add_argument("--base", default=DEFAULT_BASE, help="deck URL (default: the deck on :18091)")
    ap.add_argument("--width", type=int, default=1280)
    ap.add_argument("--height", type=int, default=720)
    return ap

def open_deck(pw, base, width, height, capture=None):
    """Launch Chrome, open the deck, wait for Reveal; optional capture dict collects console/page/request events."""
    browser = pw.chromium.launch(channel=CHANNEL, headless=True)
    ctx = browser.new_context(viewport={"width": width, "height": height}, device_scale_factor=1)
    page = ctx.new_page()
    if capture is not None:
        capture.setdefault("console", []); capture.setdefault("pageerror", []); capture.setdefault("failed", [])
        page.on("console", lambda m: capture["console"].append((m.type, m.text)) if m.type in ("error", "warning") else None)
        page.on("pageerror", lambda e: capture["pageerror"].append(str(e)))
        page.on("requestfailed", lambda r: capture["failed"].append((r.url, r.failure)) if r.failure and "ERR_ABORTED" not in str(r.failure) else None)
        page.on("response", lambda r: capture["failed"].append((r.url, r.status)) if r.status >= 400 else None)
    page.goto(base + ("" if "#" in base else "#/"), wait_until="load")
    page.wait_for_function("window.Reveal && Reveal.isReady && Reveal.isReady()", timeout=30000)
    time.sleep(0.5)
    return browser, page

def slide_list(page):
    """All horizontal slides in deck order: [{h, id, section, uncounted, iframe}]."""
    return page.evaluate("""() => Reveal.getHorizontalSlides().map((s, h) => ({
        h, id: s.id, section: s.dataset.section || null,
        uncounted: s.dataset.visibility === 'uncounted', divider: s.classList.contains('divider'),
        iframe: s.dataset.backgroundIframe || null, title: (s.querySelector('h2') || {}).textContent || '' }))""")

def goto(page, h, settle=0.25):
    page.evaluate(f"Reveal.slide({h})")
    time.sleep(settle)
    cur = page.evaluate("Reveal.getCurrentSlide().id")
    return cur

def label(page):
    return page.evaluate("(document.getElementById('sdb-slideno') || {}).textContent || ''")

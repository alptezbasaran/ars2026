"""Clicker test for every background-iframe slide: click inside the iframe (focus moves
into the animation page), then press PageDown / n / PageUp / p and check that the deck
moved. Usage: bridge_test.py [--base URL]"""
import os, sys, time
sys.path.insert(0, os.path.dirname(__file__))
from _common import *

a = parser(__doc__).parse_args()
with sync_playwright() as pw:
    browser, page = open_deck(pw, a.base, a.width, a.height)
    slides = slide_list(page); fails = 0; n = 0
    for s in slides:
        if not s["iframe"]: continue
        n += 1
        for key, expect in (("PageDown", 1), ("n", 1), ("PageUp", -1), ("p", -1)):
            goto(page, s["h"], settle=1.5)
            page.mouse.click(a.width // 2, a.height // 2); time.sleep(0.3)
            page.keyboard.press(key); time.sleep(0.5)
            got = page.evaluate("Reveal.getIndices().h") - s["h"]
            ok = got == expect
            fails += (not ok)
            print(f"{'ok ' if ok else 'FAIL'} h={s['h']:3d} {os.path.basename(s['iframe']):34s} {key:8s} -> {got:+d} (expected {expect:+d})")
    browser.close()
print(f"{n} animation slides, {fails} failures")
sys.exit(1 if fails else 0)

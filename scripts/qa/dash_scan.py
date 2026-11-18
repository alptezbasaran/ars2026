"""Em/en dash scan: qmd sources (citation entries on the publications slide excepted),
the rendered deck text including notes, and every animation page's rendered text.
Usage: dash_scan.py [--base URL] [--anim-dir slides/assets/anim]"""
import os, sys, glob, re
sys.path.insert(0, os.path.dirname(__file__))
from _common import *

ap = parser(__doc__); ap.add_argument("--src", default="slides"); ap.add_argument("--anim-dir", default="slides/assets/anim")
a = ap.parse_args()
bad = 0
for f in sorted(glob.glob(os.path.join(a.src, "index.qmd")) + glob.glob(os.path.join(a.src, "sections", "*.qmd"))):
    for i, line in enumerate(open(f, encoding="utf-8"), 1):
        if re.search(r'[–—]|&ndash;|&mdash;', line):
            if 'class="pubs"' in line or re.match(r'\s*<p>.*</p>\s*$', line): continue  # citation entries
            print(f"SRC {f}:{i}: {line.strip()[:110]}"); bad += 1
with sync_playwright() as pw:
    browser, page = open_deck(pw, a.base, a.width, a.height)
    n = page.evaluate("""() => { const t = document.querySelector('.reveal .slides').textContent; return (t.match(/[\\u2013\\u2014]/g) || []).length; }""")
    pubs = page.evaluate("""() => { const p = document.querySelector('.pubs'); return p ? (p.textContent.match(/[\\u2013\\u2014]/g) || []).length : 0; }""")
    print(f"RENDERED deck text: {n} dashes, of which {pubs} inside the publications list (exempt)")
    bad += n - pubs
    base_dir = a.base.rsplit("/", 1)[0]
    for f in sorted(glob.glob(os.path.join(a.anim_dir, "*.html"))):
        page.goto(base_dir + "/assets/anim/" + os.path.basename(f), wait_until="load"); time.sleep(0.6)
        k = page.evaluate("(document.body.innerText.match(/[\\u2013\\u2014]/g) || []).length")
        src = open(f, encoding="utf-8").read()
        # strings that render: crude but effective: count dashes outside // comments
        ks = len(re.findall(r'[–—]', re.sub(r'//[^\n]*', '', src)))
        print(f"ANIM {os.path.basename(f)}: rendered {k}, in non-comment source {ks}"); bad += k
    browser.close()
print("TOTAL offending dashes:", bad)
